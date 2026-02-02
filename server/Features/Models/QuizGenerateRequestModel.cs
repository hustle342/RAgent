namespace RAgentBackend.Features.Models
{
    public record QuizGenerateRequestModel(string SourceText, int Count = 5, string Difficulty = "Medium");
}
