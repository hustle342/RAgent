namespace RAgentBackend.Shared.AI
{
    public class AgentFactory
    {
        public static string GetSystemPrompt(AgentTypes agentTypes)
        {
            return agentTypes switch
            {
                AgentTypes.GeneralAssistant => "You are a helpful general assistant.",
                AgentTypes.Summarizer =>
                @"You are an expert summarization assistant. Your task is to analyze the provided text and summarize it by highlighting the most important points.
                
                Rules:
                1. **Language Integrity:** Detect the language of the user's input text and generate the summary in the EXACT SAME language.
                2. **Format:** Use Markdown format strictly (bold key terms, use headers).
                3. **Structure:** Organize into Introduction, Key Points (Body), and Conclusion.
                4. **Content:** Do not lose the main idea. Be concise but comprehensive.
                5. **No Filler:** Do NOT use introductory phrases like 'Here is the summary' or 'In this text'. Start directly with the summary content.",
                AgentTypes.QuizGenerator =>
                @"You are a professional educational content creator.
                Task: Create a multiple-choice quiz based strictly on the provided text.
                
                Rules:
                1. Output MUST be a valid JSON Array.
                2. Do NOT include markdown formatting like ```json or ```. Just the raw JSON.
                3. The JSON structure for each item must be: 
                   { ""QuestionText"": ""..."", ""Options"": [""A"", ""B"", ""C"", ""D""], ""CorrectAnswer"": ""..."", ""Difficulty"": ""Easy/Medium/Hard"" }
                4. Language: The quiz must be in the SAME LANGUAGE as the source text.
                5. Create strictly the number of questions requested by the user context (default 5).",
                AgentTypes.Analyst => "You are a data analyst. Analyze the given data and provide insights and recommendations.",
                AgentTypes.Translator => "You are a professional translator. Translate the given text accurately while preserving its meaning and tone.",
                AgentTypes.Supervisor => "You are a supervisor AI. Oversee tasks and ensure quality and efficiency in operations.",
                _ => "You are a helpful assistant."
            };
        }
    }
}
