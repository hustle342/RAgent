using Carter;
using Microsoft.AspNetCore.Mvc;
using RAgentBackend.Features.Models;
using RAgentBackend.Shared.AI;
using System.Text.Json;

namespace RAgentBackend.Features.QuizGeneration
{
    public class QuizGeneratorEndpoint : ICarterModule
    {
        public void AddRoutes(IEndpointRouteBuilder app)
        {
            app.MapPost("/api/quiz", HandleAsync)
                .WithName("GenerateQuiz")
                .WithTags("Quiz")
                .DisableAntiforgery();
        }

        private async Task<IResult> HandleAsync(
            [FromBody] QuizGenerateRequestModel request,
            [FromServices] IAIClient aiClient)
        {
            var userPrompt = $"Text: {request.SourceText}\n\nRequirement: Create {request.Count} questions. Difficulty: {request.Difficulty}.";
            var response = await aiClient.ProcessRequestAsync(userPrompt, AgentTypes.QuizGenerator);
            
            var cleanJson = response
                .Replace("```json", "")
                .Replace("```", "")
                .Trim();

            int startIndex = cleanJson.IndexOf('[');
            int endIndex = cleanJson.LastIndexOf(']');

            if(startIndex == -1 || endIndex == -1)
            {
                return Results.Problem("The AI response does not contain a valid JSON array.");
            }
            
            cleanJson = cleanJson.Substring(startIndex, endIndex - startIndex + 1);

            try
            {
                var questions = JsonSerializer.Deserialize<List<QuizQuestionModel>>(cleanJson, new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true 
                });

                return Results.Ok(questions);
            }
            catch (JsonException)
            {
                return Results.Problem("Failed to parse the AI response into quiz questions.");
            }
        }
    }
}
