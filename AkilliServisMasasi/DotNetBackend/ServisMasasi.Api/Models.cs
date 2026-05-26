using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace ServisMasasi.Api.Models;

public class User
{
    [Key]
    public Guid Id { get; set; } = Guid.NewGuid();
    
    [Required]
    [StringLength(100)]
    public string Username { get; set; } = string.Empty;
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}

public class Ticket
{
    [Key]
    public Guid Id { get; set; } = Guid.NewGuid();
    
    [Required]
    public Guid UserId { get; set; }
    
    [Required]
    public string UserPrompt { get; set; } = string.Empty;
    
    public string FinalResponse { get; set; } = string.Empty;
    
    [StringLength(50)]
    public string Status { get; set; } = "Pending";
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}

public class ImageLog
{
    [Key]
    public Guid Id { get; set; } = Guid.NewGuid();
    
    [Required]
    public Guid TicketId { get; set; }
    
    [Required]
    public string OriginalImagePath { get; set; } = string.Empty;
    
    public string ProcessedImagePath { get; set; } = string.Empty;
    
    public string RawOcrText { get; set; } = string.Empty;
    
    [StringLength(100)]
    public string DetectedErrorCode { get; set; } = string.Empty;
    
    [Column(TypeName = "decimal(5,2)")]
    public decimal ConfidenceScore { get; set; }
}
