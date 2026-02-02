using Carter;
using Microsoft.AspNetCore.Mvc;
using RAgentBackend.Features.Models;
using RAgentBackend.Shared.AI;

namespace RAgentBackend.Features.Summarization
{
    public class SummarizeEndpoint : ICarterModule
    {
        public void AddRoutes(IEndpointRouteBuilder app)
        {
            app.MapPost("/api/summarize", HandleAsync)
               .WithName("SummarizeText")
               .WithTags("Summarization")
               .DisableAntiforgery(); 
        }

        private async IAsyncEnumerable<string> HandleAsync(
            [FromBody] SummarizeRequestModel request,
            [FromServices] IAIClient aiClient)
        {
            if (string.IsNullOrEmpty(request.Text))
            {
                yield return "Hata: Metin boş olamaz.";
                yield break;
            }

            var stream = aiClient.StreamRequestAsync(request.Text, AgentTypes.Summarizer);

            await foreach (var token in stream)
            {
                yield return token;
            }
        }
    }

}
