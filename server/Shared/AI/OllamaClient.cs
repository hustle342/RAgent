using RAgentBackend.Shared.AI.Models;
using System.Text.Json;
using System.Text.Json.Nodes; 
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration; 
using System.Net.Http.Headers; 

namespace RAgentBackend.Shared.AI
{
    public class OllamaClient : IAIClient
    {
        private readonly HttpClient _httpClient;
        private const string modelName = "llama-3.1-8b-instant";
        private string? systemPrompt;

        public OllamaClient(HttpClient httpClient, IConfiguration configuration)
        {
            _httpClient = httpClient;
            _httpClient.BaseAddress = new Uri("https://api.groq.com/openai/v1/");

            var apiKey = configuration["GroqApiKey"];
            _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", apiKey);
        }

        public async Task<string> ProcessRequestAsync(string userMessage, AgentTypes agentType)
        {
            systemPrompt = AgentFactory.GetSystemPrompt(agentType);

            var requestBody = new
            {
                model = modelName,
                messages = new[]
                {
                    new { role = "system", content = systemPrompt },
                    new { role = "user", content = userMessage }
                },
                stream = false,
                temperature = 0.7
            };

            var jsonContent = new StringContent(
                JsonSerializer.Serialize(requestBody),
                System.Text.Encoding.UTF8,
                "application/json");

            try
            {
                var response = await _httpClient.PostAsync("chat/completions", jsonContent);
                response.EnsureSuccessStatusCode();
                var responseString = await response.Content.ReadAsStringAsync();
                using var doc = JsonDocument.Parse(responseString);
                var content = doc.RootElement
                                 .GetProperty("choices")[0]
                                 .GetProperty("message")
                                 .GetProperty("content")
                                 .GetString();

                return content ?? "Hata: Cevap boş.";
            }
            catch (HttpRequestException ex)
            {
                return $"Hata: {ex.Message}";
            }
            catch (Exception ex)
            {
                return $"Beklenmeyen hata: {ex.Message}";
            }
        }

        public async IAsyncEnumerable<string> StreamRequestAsync(string userMessage, AgentTypes agentType)
        {
            systemPrompt = AgentFactory.GetSystemPrompt(agentType);

            var requestBody = new
            {
                model = modelName,
                messages = new[]
                {
                    new { role = "system", content = systemPrompt },
                    new { role = "user", content = userMessage }
                },
                stream = true,
                temperature = 0.7 
            };

            var jsonContent = new StringContent(
                JsonSerializer.Serialize(requestBody),
                System.Text.Encoding.UTF8,
                "application/json");

            using var response = await _httpClient
                .SendAsync(new HttpRequestMessage
                {
                    Method = HttpMethod.Post,
                    RequestUri = new Uri("chat/completions", UriKind.Relative),
                    Content = jsonContent
                }, HttpCompletionOption.ResponseHeadersRead);

            response.EnsureSuccessStatusCode();

            using var stream = await response.Content.ReadAsStreamAsync();
            using var reader = new StreamReader(stream);

            while (!reader.EndOfStream)
            {
                var line = await reader.ReadLineAsync();
                if (string.IsNullOrWhiteSpace(line)) continue;

                if (line.StartsWith("data: "))
                {
                    var data = line.Substring(6); 
                    if (data == "[DONE]") break; 


                    using var doc = JsonDocument.Parse(data);
                    var choice = doc.RootElement.GetProperty("choices")[0];

                    if (choice.GetProperty("delta").TryGetProperty("content", out var contentElement))
                    {
                        yield return contentElement.GetString() ?? string.Empty;
                    }
                }
            }
        }
    }
}