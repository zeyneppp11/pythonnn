using Microsoft.EntityFrameworkCore;
using ServisMasasi.Api.Models;

namespace ServisMasasi.Api.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<User> Users { get; set; } = default!;
    public DbSet<Ticket> Tickets { get; set; } = default!;
    public DbSet<ImageLog> ImageLogs { get; set; } = default!;
    public DbSet<KnowledgeBase> KnowledgeBases { get; set; } = default!;
}