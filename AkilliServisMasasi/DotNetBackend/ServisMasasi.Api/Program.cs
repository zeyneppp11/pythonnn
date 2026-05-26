using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.FileProviders;
using ServisMasasi.Api.Data;
using ServisMasasi.Api.Models;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyHeader()
              .AllowAnyMethod();
    });
});

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();

builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));

var app = builder.Build();

// OTOMATİK TABLO OLUŞTURMA VE VERİ EKLEME MANTIĞI
using (var scope = app.Services.CreateScope())
{
    var context = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    
    // Bu satır veritabanında tablolar yoksa otomatik olarak oluşturur!
    context.Database.EnsureCreated();

    if (!context.KnowledgeBases.Any())
    {
        context.KnowledgeBases.AddRange(
            new KnowledgeBase
            {
                Id = Guid.NewGuid(),
                ErrorCode = "ORA-01017",
                Category = "Database",
                SolutionText = "[Oracle DB Uzmanı Çözümü]: Geçersiz kullanıcı adı/şifre veya yetki eksikliği. Tablespace üzerindeki ilgili kullanıcının kilidini (ALTER USER username ACCOUNT UNLOCK) kontrol edin ve CONNECT, RESOURCE rollerinin tanımlandığından emin olun."
            },
            new KnowledgeBase
            {
                Id = Guid.NewGuid(),
                ErrorCode = "0x0000007B",
                Category = "Windows Server",
                SolutionText = "[Windows Server Uzmanı Çözümü]: INACCESSIBLE_BOOT_DEVICE mavi ekran hatası. Depolama denetleyicisi (AHCI/RAID) sürücülerini güncelleyin, güvenli modda başlatarak Windows Event Log (Sistem) kayıtlarını ve dump dökümlerini inceleyin."
            }
        );
        context.SaveChanges();
    }
}

app.UseCors("AllowAll");

var uploadsPath = Path.Combine(Directory.GetCurrentDirectory(), "Uploads");
if (!Directory.Exists(uploadsPath)) Directory.CreateDirectory(uploadsPath);

app.UseStaticFiles(new StaticFileOptions
{
    FileProvider = new PhysicalFileProvider(uploadsPath),
    RequestPath = "/images"
});

app.UseAuthorization();
app.MapControllers();

app.Run();
