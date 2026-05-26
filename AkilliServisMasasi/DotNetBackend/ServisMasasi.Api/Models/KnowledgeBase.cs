using System.ComponentModel.DataAnnotations;

namespace ServisMasasi.Api.Models;

public class KnowledgeBase
{
    [Key]
    public Guid Id { get; set; } = Guid.NewGuid();

    [Required]
    [MaxLength(100)]
    public string ErrorCode { get; set; } = string.Empty;

    [Required]
    [MaxLength(50)]
    public string Category { get; set; } = string.Empty;

    [Required]
    public string SolutionText { get; set; } = string.Empty;

    [Required]
    [MaxLength(100)]
    public string CreatedBy { get; set; } = "System";

    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
