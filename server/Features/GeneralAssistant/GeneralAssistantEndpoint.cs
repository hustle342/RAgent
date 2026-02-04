using Microsoft.AspNetCore.Mvc;
using RAgentBackend.Shared.AI;
using RAgentBackend.Features.Models;

namespace RAgentBackend.Features.GeneralAssistant
{
    public class GeneralAssistantEndpoint
    {
        public void AddRoutes(IEndpointRouteBuilder app)
        {
            app.MapPost("/api/chat/general", HandleAsync)
               .WithName("GeneralChat")
               .WithTags("Chat");
        }

        private async IAsyncEnumerable<string> HandleAsync(
            [FromBody] GeneralAssistantRequestModel request,
            [FromServices] IAIClient aiClient)
        {
            if (string.IsNullOrWhiteSpace(request.Message))
            {
                yield return "Lütfen bir mesaj yazın.";
                yield break;
            }

            var stream = aiClient.StreamRequestAsync(request.Message, AgentTypes.GeneralAssistant);

            await foreach (var token in stream)
            {
                yield return token;
            }
        }
    }
}
