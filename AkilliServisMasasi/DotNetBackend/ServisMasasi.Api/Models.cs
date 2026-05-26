using System;

namespace ServisMasasi.Api.Models
{
    public class User
    {
        public int Id { get; set; }
        public string Username { get; set; } = string.Empty;
        public string Email { get; set; } = string.Empty;
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    }

    public class ImageLog
    {
        public int Id { get; set; }
        public int? UserId { get; set; }
        public string ImagePath { get; set; } = string.Empty;
        public DateTime UploadedAt { get; set; } = DateTime.UtcNow;
    }

    public class OcrResult
    {
        public int Id { get; set; }
        public int? ImageLogId { get; set; }
        public string RawOcrText { get; set; } = string.Empty;
        public string DetectedErrorCode { get; set; } = string.Empty;
        public float ConfidenceScore { get; set; }
        public DateTime ProcessedAt { get; set; } = DateTime.UtcNow;
    }

    public class KnowledgeBase
    {
        public int Id { get; set; }
        public string ErrorCode { get; set; } = string.Empty;
        public string Category { get; set; } = string.Empty;
        public string SolutionText { get; set; } = string.Empty;
        public float[]? Embedding { get; set; }
    }
}
