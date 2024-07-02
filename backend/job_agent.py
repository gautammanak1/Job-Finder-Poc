from pydantic import Field
from uagents import Agent, Context, Protocol, Model
from ai_engine import UAgentResponse, UAgentResponseType
import requests

job_protocol = Protocol(name="job_protocol")

class JobRequest(Model):
    job_description: str = Field(description="Give details of job you are looking for")

async def get_job_details(job_role, rapidapi_key):
    url = "https://indeed11.p.rapidapi.com/"
    payload = {
        "search_terms": job_role,
        "location": "United States",
        "page": "1"
    }
    headers = {
        'x-rapidapi-key': rapidapi_key,
        'x-rapidapi-host': "indeed11.p.rapidapi.com",
        'Content-Type': "application/json"
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.status_code, "message": response.text}

rapidapi_key = "911d4d6013mshe47e761d58e4b09p11e35djsn88fd7c2d401c"

@job_protocol.on_message(model=JobRequest, replies={UAgentResponse})
async def load_job(ctx: Context, sender: str, msg: JobRequest):
    ctx.logger.info(f"Received job request: {msg.job_description}")
    
    try:
        details = await get_job_details(msg.job_description, rapidapi_key)
        ctx.logger.info(f"Job details for {msg.job_description}: {details}")
        message = ""
        for detail in details:
            ctx.logger.info(detail)
            job_url = detail['url']
            job_title = detail['job_title']
            company_name = detail['company_name']
            location = detail['location']
            salary = detail['salary']
            summary = detail['summary']
            job_date = detail.get('date', 'Just posted')

            message += (f"<a href='{job_url}'>{job_title}</a> - {job_date}\n"
                        f"Company: {company_name}\n"
                        f"Location: {location}\n"
                        f"Salary: {salary}\n"
                        f"Summary: {summary}\n\n")
    except Exception as e:
        ctx.logger.error(f"An error occurred while fetching job details: {e}")
        message = f"An unexpected error occurred: {e}"

    await ctx.send(sender, UAgentResponse(message=message, type=UAgentResponseType.FINAL))

agent = Agent()
agent.include(job_protocol, publish_manifest=True)
