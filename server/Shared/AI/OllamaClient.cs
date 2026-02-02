using RAgentBackend.Shared.AI.Models;
using System.Text.Json;
using System.Threading.Tasks;

namespace RAgentBackend.Shared.AI
{
    public class OllamaClient : IAIClient
    {
        private readonly HttpClient _httpClient;
        private const string modelName = "llama3.1";
        private string? systemPrompt;
        public OllamaClient(HttpClient httpClient)
        {
            _httpClient = httpClient;
            _httpClient.BaseAddress = new Uri("http://localhost:11434/");
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
                options = new
                {
                    temperature = 0.7
                }
            };

            var jsonContent = new StringContent(
                JsonSerializer.Serialize(requestBody),
                System.Text.Encoding.UTF8,
                "application/json");


            try
            {
                var response = await _httpClient.PostAsync("api/chat", jsonContent);
                response.EnsureSuccessStatusCode();
                var responseString = await response.Content.ReadAsStringAsync();
                var ollamaResponse = JsonSerializer.Deserialize<OllamaResponseModel>(responseString);

                return ollamaResponse?.Message?.Content ?? "Hata: Cevap alınamadı.";
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
                options = new
                {
                    temperature = 0.7
                }
            };

            var jsonContent = new StringContent(
                JsonSerializer.Serialize(requestBody),
                System.Text.Encoding.UTF8,
                "application/json");

             using var response = await _httpClient
                 .SendAsync(new HttpRequestMessage
                 {
                     Method = HttpMethod.Post,
                     RequestUri = new Uri("api/chat", UriKind.Relative),
                     Content = jsonContent
                 }, HttpCompletionOption.ResponseHeadersRead);
             
             response.EnsureSuccessStatusCode();

             using var stream = await response.Content.ReadAsStreamAsync();
             using var reader = new StreamReader(stream);

             while (!reader.EndOfStream)
             {
                 var line = await reader.ReadLineAsync();

                 if(string.IsNullOrWhiteSpace(line)) continue;

                 var jsonNode = JsonSerializer.Deserialize<OllamaResponseModel>(line);

                 yield return jsonNode?.Message?.Content ?? string.Empty;
             }
        }
    }
}
