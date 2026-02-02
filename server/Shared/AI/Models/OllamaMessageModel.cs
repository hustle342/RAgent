using System.Text.Json.Serialization;

namespace RAgentBackend.Shared.AI.Models
{
    public class OllamaMessageModel
    {
        [JsonPropertyName("content")]
        public string? Content { get; set; }
    }
}
