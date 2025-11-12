<!-- 16fcddb9-fa7b-429f-9728-051cb770f5e9 b406c2ec-dd02-424d-8321-2f5293c40d20 -->
# MongoDB Atlas Setup Plan

## Steps

1. Create Atlas Account and Project

- Sign up / log in at https://www.mongodb.com/cloud/atlas
- Create a new project named “Network Traffic Analyzer” (or similar)

2. Provision a Shared Cluster

- Choose the free M0 tier
- Select AWS in a close region (e.g., us-west-2 if your Render service is in Oregon)
- Finish cluster creation

3. Configure Database Access

- Under Database Access, add a database user with `Read and write to any database`
- Record the username and password (you’ll need them for the connection string)

4. Allow Network Access

- Under Network Access, add IP address `0.0.0.0/0` temporarily for testing, or list Render outbound IPs if preferred

5. Obtain Connection String

- Click “Connect” → “Connect your application”
- Copy the SRV URI (e.g., `mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`)
- URL-encode the password if it contains special characters

6. Configure Environment Variables

- On Render (backend service): set `NTA_MONGODB_URI` to the URI and `NTA_MONGODB_DATABASE` to your database name
- Locally/Vercel: set `NEXT_PUBLIC_API_URL` to your backend URL; no MongoDB settings needed on Vercel unless running the backend locally

7. Deploy and Verify

- Redeploy/restart the Render backend so the new env vars load
- Tail logs to confirm “Connected to MongoDB successfully”
- Test the `/api/files` endpoint or upload a sample PCAP to verify persistence