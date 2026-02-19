//using Microsoft.AspNetCore.DataProtection.KeyManagement;
//using System.Net.Http.Headers;

//namespace RAgentBackend.Shared.AI
//{
//    public class GroqClient : IAIClient
//    {
//        private readonly HttpClient _httpClient;
//        private readonly string _apiKey;

//        public GroqClient(HttpClient httpClient, IConfiguration configuration)
//        {
//            _httpClient = httpClient;
//            _httpClient.BaseAddress = new Uri("https://api.groq.com/openai/v1/");
//            _apiKey = configuration.GetValue<String>("GroqApiKey",string.Empty);
//            _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", _apiKey);


//        }
//    }
//}
