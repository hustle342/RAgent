namespace RAgentBackend.Shared.AI
{
    public interface IAIClient
    {
        Task<string> ProcessRequestAsync(string userMessage, AgentTypes agentType);
        IAsyncEnumerable<string> StreamRequestAsync(string userMessage, AgentTypes agentType);
    }
}
