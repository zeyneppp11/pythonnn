using Microsoft.EntityFrameworkCore;
using ServisMasasi.Api.Models;

namespace ServisMasasi.Api
{
    public class AppDbContext : DbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

        public DbSet<User> Users { get; set; }
        public DbSet<ImageLog> ImageLogs { get; set; }
        public DbSet<OcrResult> OcrResults { get; set; }
        public DbSet<KnowledgeBase> KnowledgeBases { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);
            
            // PostgreSQL büyük-küçük harf duyarlılığı için tablo isimlerini formla eşitliyoruz
            modelBuilder.Entity<User>().ToTable("Users");
            modelBuilder.Entity<ImageLog>().ToTable("ImageLogs");
            modelBuilder.Entity<OcrResult>().ToTable("OcrResults");
            modelBuilder.Entity<KnowledgeBase>().ToTable("KnowledgeBases");
        }
    }
}
