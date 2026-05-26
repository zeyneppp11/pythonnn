using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Text.Json;
using ServisMasasi.Api.Data;
using ServisMasasi.Api.Models;

namespace ServisMasasi.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class TicketController : ControllerBase
{
    private readonly AppDbContext _context;
    private readonly HttpClient _httpClient;

    public TicketController(AppDbContext context)
    {
        _context = context;
        _httpClient = new HttpClient();
    }

    [HttpPost("upload-screenshot")]
    public async Task<IActionResult> UploadScreenshot([FromForm] IFormFile? file, [FromForm] string? userPrompt, [FromForm] Guid userId)
    {
        string promptText = userPrompt ?? "Görsel yüklendi.";
        string expertSolution = "İşlem yapılıyor...";
        string detectedCode = "UNKNOWN";
        string rawOcrText = "";
        string processedPathForDb = "";
        string webImageResponseUrl = ""; 
        string filePath = "";

        var uploadsFolder = Path.Combine(Directory.GetCurrentDirectory(), "Uploads");
        if (!Directory.Exists(uploadsFolder)) Directory.CreateDirectory(uploadsFolder);

        if (file != null && file.Length > 0)
        {
            filePath = Path.Combine(uploadsFolder, file.FileName);
            using (var stream = new FileStream(filePath, FileMode.Create))
            {
                await file.CopyToAsync(stream);
            }

            try
            {
                var pythonApiUrl = "http://127.0.0.1:8000/process-image/";
                using var requestContent = new MultipartFormDataContent();
                using var fileStream = file.OpenReadStream();
                using var streamContent = new StreamContent(fileStream);
                requestContent.Add(streamContent, "file", file.FileName);

                var pythonResponse = await _httpClient.PostAsync(pythonApiUrl, requestContent);
                if (pythonResponse.IsSuccessStatusCode)
                {
                    var responseString = await pythonResponse.Content.ReadAsStringAsync();
                    var aiResult = JsonSerializer.Deserialize<PythonAiResult>(responseString, new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
                    
                    if (aiResult != null)
                    {
                        rawOcrText = aiResult.raw_text ?? "";
                        detectedCode = aiResult.detected_error_code ?? "UNKNOWN";
                        
                        string pythonImagePath = Path.Combine(Directory.GetCurrentDirectory(), "..", "PythonAiService", aiResult.processed_image_path);
                        if (System.IO.File.Exists(pythonImagePath))
                        {
                            string processedFileName = "ai_" + file.FileName;
                            string newDestination = Path.Combine(uploadsFolder, processedFileName);
                            System.IO.File.Copy(pythonImagePath, newDestination, true);
                            
                            processedPathForDb = newDestination;
                            webImageResponseUrl = $"http://localhost:5121/images/{processedFileName}"; 
                        }
                    }
                }
            }
            catch
            {
                rawOcrText = "Python AI Servisine erişilemedi.";
            }
        }

        string searchCode = "UNKNOWN";
        string fullSearchText = (promptText + " " + rawOcrText + " " + detectedCode).ToUpper();

        if (fullSearchText.Contains("ORA-01017")) searchCode = "ORA-01017";
        else if (fullSearchText.Contains("0X0000007B")) searchCode = "0x0000007B";

        if (searchCode != "UNKNOWN")
        {
            var knowledge = await _context.KnowledgeBases
                .FirstOrDefaultAsync(k => k.ErrorCode.ToLower() == searchCode.ToLower());

            if (knowledge != null) expertSolution = knowledge.SolutionText;
            else expertSolution = $"[{searchCode}] hatası tespit edildi fakat bilgi bankasında döküman bulunamadı.";
        }
        else
        {
            expertSolution = "[Genel Destek Çözümü]: Belirli bir uzman hata kodu (ORA-01017 veya 0x0000007B) tespit edilemedi. Lütfen sistem yöneticinizle iletişime geçin.";
        }

        var ticket = new Ticket
        {
            UserId = userId,
            UserPrompt = promptText,
            FinalResponse = expertSolution,
            Status = "Success"
        };
        _context.Tickets.Add(ticket);

        var imageLog = new ImageLog
        {
            TicketId = ticket.Id,
            OriginalImagePath = filePath,
            ProcessedImagePath = processedPathForDb,
            RawOcrText = rawOcrText,
            DetectedErrorCode = searchCode,
            ConfidenceScore = 100
        };
        _context.ImageLogs.Add(imageLog);
        await _context.SaveChangesAsync();

        return Ok(new { TicketId = ticket.Id, Response = expertSolution, ErrorCode = searchCode, AiImage = webImageResponseUrl });
    }
}

public class PythonAiResult
{
    public string raw_text { get; set; } = string.Empty;
    public string detected_error_code { get; set; } = string.Empty;
    public string processed_image_path { get; set; } = string.Empty;
}