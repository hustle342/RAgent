namespace RAgentBackend.Features.Models
{
    public class QuizQuestionModel
    {
        public string QuestionText { get; set; } = string.Empty;
        public List<string> Options { get; set; } = new List<string>();
        public string CorrectAnswer { get; set; } = string.Empty;
        public string Difficulty { get; set; } = string.Empty;
    }
}
