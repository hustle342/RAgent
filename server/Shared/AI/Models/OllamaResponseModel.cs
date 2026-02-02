using System.Text.Json.Serialization;

namespace RAgentBackend.Shared.AI.Models
{
    public class OllamaResponseModel
    {
        [JsonPropertyName("message")]
        public OllamaMessageModel? Message { get; set; }
    }
}
