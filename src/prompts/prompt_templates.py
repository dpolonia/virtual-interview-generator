# Prompt templates for various functions

# Persona generation prompt template
INTERVIEWER_PERSONA_PROMPT = """
You will help me generate virtual interviews for a research project on "The Role of Business Consulting Firms in the Era of Artificial Intelligence." I have an interview script with questions for various stakeholder groups and need to simulate realistic interviews.

Please create a detailed persona for an interviewer with the following characteristics:
- A name
- Age (30-65)
- Professional background in consulting, research, or journalism
- Interview style characteristics (e.g., formal, conversational, detail-oriented)
- Level of expertise in AI and consulting
- Educational background
- Years of experience conducting interviews
- Personal communication style

Make this persona realistic and provide enough detail that I can understand how they would conduct an interview.
"""

INTERVIEWEE_PERSONA_PROMPT = """
Create a detailed persona for a {category} to be interviewed for a research project on "The Role of Business Consulting Firms in the Era of Artificial Intelligence."

Include the following details:
- Name
- Age (appropriate for their role)
- Position/Title
- Company/Organization (fictional but realistic)
- Years of experience
- Educational background
- Brief professional history
- Areas of expertise
- Personal communication style
- Views on AI (ranging from enthusiastic to skeptical)

Make this persona realistic and detailed. Their background should be consistent with the role of {category}.
"""

INTERVIEW_GENERATION_PROMPT = """
I'd like you to simulate an interview between an interviewer and a stakeholder in the consulting industry about AI adoption.

INTERVIEWER PERSONA:
{interviewer_details}

STAKEHOLDER PERSONA:
{interviewee_details}

INTERVIEW SCRIPT:
{script}

Please simulate a realistic interview conversation following this exact script. The conversation should:
1. Start with the introduction
2. Cover the demographic questions
3. Proceed through each research question section in order
4. Include natural follow-up questions when appropriate
5. End with the closing

The stakeholder's responses should reflect their background, expertise, and views on AI as defined in their persona. The interviewer should maintain their defined interview style.

Important: Follow the script questions precisely - don't skip any sections or questions. The goal is to generate a realistic interview that addresses all the research questions.
"""

XML_FORMATTING_PROMPT = """
Please format the following interview conversation into XML format according to this structure:

<conversation_set>
  <conversation id="{interview_id}">
    <personas>
      <interviewer>
        {interviewer_details}
      </interviewer>
      <respondent>
        {interviewee_details}
      </respondent>
    </personas>
    <dialogue>
      <interviewer_line>[Line from the interviewer]</interviewer_line>
      <respondent_line>[Response from the stakeholder]</respondent_line>
      [Repeat interviewer_line and respondent_line for the entire conversation]
    </dialogue>
  </conversation>
</conversation_set>

Here's the interview conversation:

{interview_text}
"""

ANALYSIS_PROMPT = """
Analyze the following interview between an interviewer and a stakeholder in the consulting industry about AI adoption:

{interview_text}

Please provide the following analysis:

1. Summary of key points raised by the respondent
2. Notable quotes that could be useful for academic research
3. Main attitudes expressed toward AI adoption in consulting
4. Specific insights related to each research question:
   - RQ1: How established is AI adoption within the consulting industry?
   - RQ2: What are the current trends in the consulting market in Portugal?
   - RQ3: How does AI affect the business of consulting firms in terms of automation and internalisation of knowledge by clients?
   - RQ4: What ethical risks and concerns are associated with integrating AI in consulting?
5. Any contradictions or interesting nuances in the respondent's views
6. Authenticity assessment - how realistic the responses appear

Provide a comprehensive analysis that could be used for academic research.
"""

# New prompt for enhancing FinePersonas
FINEPERSONA_ENHANCEMENT_PROMPT = """
Below is a high-level description of a persona. Please enhance this description into a more detailed persona suitable for a research interview about AI in consulting.

Original persona description:
{persona_text}

Please provide a detailed enhancement that includes:
- A suitable full name
- Age range
- Job title and company (fictional but realistic)
- Years of experience
- Educational background
- Specific expertise areas
- Communication style
- Views on AI technology adoption (based on the persona's field)

Format the enhanced persona as a detailed first-person description that can be used for a realistic interview simulation.
"""