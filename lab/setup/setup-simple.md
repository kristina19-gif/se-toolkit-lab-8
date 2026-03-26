# Lab setup

- [1. Required steps](#1-required-steps)
  - [1.1. Set up your fork](#11-set-up-your-fork)
    - [1.1.1. Fork the course instructors' repo](#111-fork-the-course-instructors-repo)
    - [1.1.2. Go to your fork](#112-go-to-your-fork)
    - [1.1.3. Enable issues](#113-enable-issues)
    - [1.1.4. Add a classmate as a collaborator](#114-add-a-classmate-as-a-collaborator)
    - [1.1.5. Protect your `main` branch](#115-protect-your-main-branch)
  - [1.2. Clone your fork and set up the environment](#12-clone-your-fork-and-set-up-the-environment)
  - [1.3. Stop Lab 7 services](#13-stop-lab-7-services)
  - [1.4. Start the services locally](#14-start-the-services-locally)
  - [1.5. Populate the database](#15-populate-the-database)
  - [1.6. Verify the local deployment](#16-verify-the-local-deployment)
  - [1.7. Deploy to your VM](#17-deploy-to-your-vm)
  - [1.8. Set up SSH for the autochecker](#18-set-up-ssh-for-the-autochecker)
  - [1.9. Set up LLM access (Qwen Code API)](#19-set-up-llm-access-qwen-code-api)
  - [1.10. Coding agent](#110-coding-agent)

## 1. Required steps

> [!NOTE]
> This lab builds on the same tools and setup from previous labs.
> If you completed Labs 4–7, most tools are already installed.
> The main changes are: a new repo, cleaning up Lab 7, and deploying the base system.

> [!IMPORTANT]
> In this lab, you start with only the **base LMS system** (backend, database, dashboard). You will add the AI agent, chat clients, and observability tools **during the tasks** — not during setup. The setup just gets the foundation running.

> [!NOTE]
> This lab needs your university email and GitHub alias in the Autochecker bot <https://t.me/auchebot>. If you haven't registered, do so now. If you want to change something, contact your TA or try `/reset` in the autochecker bot.

> [!TIP]
> In the instructions below, values you need to replace are marked like this: **`YOUR_VALUE`**. Replace the entire placeholder (including the `<` and `>` if present) with your actual value.

> [!TIP]
> First ask your [coding agent](#110-coding-agent), then ask the TA.

### 1.1. Set up your fork

#### 1.1.1. Fork the course instructors' repo

1. Fork the [lab's repo](https://github.com/inno-se-toolkit/se-toolkit-lab-8).

We refer to your fork as `fork` and to the original repo as `upstream`.

#### 1.1.2. Go to your fork

1. Go to your fork: `https://github.com/`**`YOUR_GITHUB_USERNAME`**`/se-toolkit-lab-8`.

#### 1.1.3. Enable issues

1. [Enable issues](../../wiki/github.md#enable-issues).

#### 1.1.4. Add a classmate as a collaborator

1. [Add a collaborator](../../wiki/github.md#add-a-collaborator) — your partner.
2. Your partner should add you as a collaborator in their repo.

#### 1.1.5. Protect your `main` branch

1. [Protect a branch](../../wiki/github.md#protect-a-branch).

### 1.2. Clone your fork and set up the environment

1. Clone your fork to your local machine:

   ```terminal
   git clone --recurse-submodules https://github.com/YOUR_GITHUB_USERNAME/se-toolkit-lab-8
   ```

   Replace **`YOUR_GITHUB_USERNAME`** with your GitHub username.

   > [!NOTE]
   > The `--recurse-submodules` flag clones the Qwen Code API [submodule](../../wiki/git.md#submodule) included in the repository.

2. Open the forked repo in `VS Code`.

3. Go to `VS Code Terminal`, [check that the current directory is `se-toolkit-lab-8`](../../wiki/shell.md#check-the-current-directory-is-directory-name), and install `Python` dependencies:

   ```terminal
   uv sync --dev
   ```

4. Create the environment file:

   ```terminal
   cp .env.docker.example .env.docker.secret
   ```

5. Configure the autochecker API credentials.

   The ETL pipeline fetches data from the autochecker dashboard API.
   Open `.env.docker.secret` and set:

   ```text
   AUTOCHECKER_API_LOGIN=YOUR_EMAIL@innopolis.university
   AUTOCHECKER_API_PASSWORD=YOUR_GITHUB_USERNAMEYOUR_TELEGRAM_ALIAS
   ```

   Replace **`YOUR_EMAIL`**, **`YOUR_GITHUB_USERNAME`**, and **`YOUR_TELEGRAM_ALIAS`** with your actual values. Example: if your GitHub username is `johndoe` and your Telegram alias is `jdoe`, the password is `johndoejdoe`.

   > [!IMPORTANT]
   > The credentials must match your autochecker bot registration.

6. Set `LMS_API_KEY` — this is the **backend API key** that protects your LMS endpoints (used for `Authorization: Bearer` in Swagger and the frontend). It is **not** the LLM key — that comes later.

   ```text
   LMS_API_KEY=set-it-to-something-and-remember-it
   ```

7. Set `QWEN_CODE_API_KEY` — the Qwen Code API is included as a Docker Compose service. You just need to set your API key:

   ```text
   QWEN_CODE_API_KEY=your-qwen-api-key
   ```

   If you don't have a Qwen API key yet, see [step 1.9](#19-set-up-llm-access-qwen-code-api).

### 1.3. Stop Lab 7 services

> [!IMPORTANT]
> Labs 7 and 8 use the same ports (42001–42005). You **must** stop Lab 7 containers before starting Lab 8.

**Locally:**

```terminal
cd ../se-toolkit-lab-7
docker compose --env-file .env.docker.secret down
cd ../se-toolkit-lab-8
```

**On your VM** (do this now so you don't forget):

```terminal
ssh YOUR_VM_USERNAME@YOUR_VM_IP
cd ~/se-toolkit-lab-7
docker compose --env-file .env.docker.secret down
```

Replace **`YOUR_VM_USERNAME`** and **`YOUR_VM_IP`** with your values.

> [!NOTE]
> You must use `--env-file .env.docker.secret` — without it, `docker compose down` will fail because the compose file references required variables.

### 1.4. Start the services locally

1. (`Windows`/`macOS`) Make sure [Docker Desktop](../../wiki/docker.md#start-docker) is running.

2. Start the services in the background:

   ```terminal
   docker compose --env-file .env.docker.secret up --build -d
   ```

3. Check that the containers are running:

   ```terminal
   docker compose --env-file .env.docker.secret ps --format "table {{.Service}}\t{{.Status}}"
   ```

   You should see the base services running:

   ```terminal
   SERVICE           STATUS
   backend           Up 50 seconds
   caddy             Up 49 seconds
   client-web-react  Up 49 seconds (exited)
   pgadmin           Up 50 seconds
   postgres          Up 55 seconds (healthy)
   qwen-code-api     Up 50 seconds (healthy)
   ```

   > [!NOTE]
   > `client-web-react` exits after copying its build output — that's normal. Caddy serves the static files.

> <h3>Troubleshooting</h3>
>
> **Port conflict (`port is already allocated`).**
>
> First, check what's using the port:
>
> ```terminal
> docker ps
> ```
>
> This shows all running containers and their ports. Look for containers using ports 42001–42005 — they're likely leftover from a previous lab. Stop them:
>
> ```terminal
> docker stop <container-name>
> ```
>
> If that doesn't help, make sure you stopped Lab 7 services (step 1.3), or [clean up `Docker`](../../wiki/docker.md#clean-up-docker) and try again.
>
> **Containers exit immediately.**
>
> Rebuild all containers from scratch:
>
> ```terminal
> docker compose --env-file .env.docker.secret down -v
> docker compose --env-file .env.docker.secret up --build -d
> ```
>
> **DNS resolution errors (`getaddrinfo EAI_AGAIN`).**
>
> If you see DNS errors like `getaddrinfo EAI_AGAIN registry.npmjs.org`, `Docker` can't resolve domain names. This is a university network DNS issue. Add Google DNS to `Docker`:
>
> ```terminal
> echo '{"dns": ["8.8.8.8", "8.8.4.4", "1.1.1.1"]}' \
>   | jq \
>   | sudo tee /etc/docker/daemon.json
>
> sudo systemctl restart docker
> ```
>
> Then run the `docker compose up` command again.
>
> **Docker Hub rate limits (`Too many requests`).**
>
> If you're building outside the university network and hit Docker Hub rate limits, set the registry prefix to empty in `.env.docker.secret`:
>
> ```text
> REGISTRY_PREFIX_DOCKER_HUB=
> ```
>
> This is only needed outside the university. On campus, the default harbor cache avoids rate limits.

### 1.5. Populate the database

The database starts empty. You need to run the ETL pipeline to populate it with data from the autochecker API.

1. Open in a browser: `http://localhost:42002/docs`

   You should see the Swagger UI page.

2. [Authorize in Swagger](../../wiki/swagger.md#authorize-in-swagger-ui) with the `LMS_API_KEY` you set in `.env.docker.secret`.

3. Run the ETL sync by calling `POST /pipeline/sync` in Swagger UI.

   You should get a response showing the number of items and logs loaded:

   ```json
   {
     "new_records": 120,
     "total_records": 9502
   }
   ```

   > [!NOTE]
   > The exact numbers depend on how much data the autochecker API has.
   > As long as both numbers are greater than 0, the sync worked.

4. Verify data by calling `GET /items/`.

   You should get a non-empty array of items.

> [!IMPORTANT]
> Without this step, all analytics endpoints return empty results and the agent will have no data to work with.

### 1.6. Verify the local deployment

1. Open `http://localhost:42002/docs` in a browser.

   You should see the Swagger UI with all endpoints.

2. Open `http://localhost:42002/` in a browser.

   You should see the React dashboard. Enter your API key to connect.

3. Switch to the **Dashboard** tab.

   You should see charts with analytics data (submissions timeline, score distribution, group performance, task pass rates).

4. Verify the Qwen Code API is working:

   ```terminal
   curl -s http://localhost:42002/utils/llm-api/models -H "Authorization: Bearer YOUR_QWEN_CODE_API_KEY" | head -c 100
   ```

   You should see a JSON response with model information.

> [!IMPORTANT]
> If the dashboard shows no data or errors, make sure:
>
> - The ETL sync completed successfully (step 1.5)
> - You entered the correct API key in the frontend
> - Try selecting a different lab in the dropdown

### 1.7. Deploy to your VM

The autochecker tests your deployment on your **VM**. You need to deploy the same services there.

1. [Connect to the VM](../../wiki/vm-access.md#connect-to-the-vm-as-the-user-user-local).

2. Make sure Lab 7 is stopped (if you haven't done this in step 1.3):

   ```terminal
   cd ~/se-toolkit-lab-7 && docker compose --env-file .env.docker.secret down
   cd ~
   ```

3. Clone your fork on the VM:

   ```terminal
   git clone --recurse-submodules https://github.com/YOUR_GITHUB_USERNAME/se-toolkit-lab-8 ~/se-toolkit-lab-8
   ```

   Replace **`YOUR_GITHUB_USERNAME`** with your GitHub username.

4. Create the environment file:

   ```terminal
   cd ~/se-toolkit-lab-8
   cp .env.docker.example .env.docker.secret
   ```

5. Edit `.env.docker.secret` — set the same credentials as in your local file:

   ```terminal
   nano .env.docker.secret
   ```

   Set `AUTOCHECKER_API_LOGIN`, `AUTOCHECKER_API_PASSWORD`, `LMS_API_KEY`, and `QWEN_CODE_API_KEY`.

6. Configure Docker DNS (required on most university VMs):

   ```terminal
   echo '{"dns": ["8.8.8.8", "8.8.4.4", "1.1.1.1"]}' \
     | jq \
     | sudo tee /etc/docker/daemon.json
   
   sudo systemctl restart docker
   ```

   > [!NOTE]
   > Without this, Docker builds will fail with `getaddrinfo EAI_AGAIN` errors because the university network DNS can't resolve external registries.

7. Start the services:

   ```terminal
   docker compose --env-file .env.docker.secret up --build -d
   ```

   > <h3>Troubleshooting</h3>
   >
   > The same troubleshooting advice as when [starting the services locally](#14-start-the-services-locally).

8. Populate the database:

   ```terminal
   curl -X POST http://localhost:42002/pipeline/sync -H "Authorization: Bearer YOUR_LMS_API_KEY" -H "Content-Type: application/json" -d '{}'
   ```

   Replace **`YOUR_LMS_API_KEY`** with the value you set in `.env.docker.secret`.

9. Verify the deployment:

   ```terminal
   curl -s http://localhost:42002/items/ -H "Authorization: Bearer YOUR_LMS_API_KEY" | head -c 200
   ```

   You should see a JSON array of items.

> [!IMPORTANT]
> Keep the services running on your VM. The autochecker will query your deployment during evaluation.

### 1.8. Set up SSH for the autochecker

The autochecker needs to SSH into your VM as **your main user** to run checks.

> [!NOTE]
> If you completed Lab 6 Task 3, this is already done. Verify by checking with the autochecker bot — if the setup check passes, skip this step.

1. On your VM, add the autochecker's SSH public key:

   ```terminal
   mkdir -p ~/.ssh
   echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKiL0DDQZw7L0Uf1c9cNlREY7IS6ZkIbGVWNsClqGNCZ se-toolkit-autochecker' >> ~/.ssh/authorized_keys
   chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys
   ```

2. Register your VM username with the autochecker bot if you haven't already.

   In the Telegram bot, when prompted for your VM username, run `whoami` on your VM and reply with the output.

### 1.9. Set up LLM access (Qwen Code API)

The Qwen Code API is included as a Docker Compose service in this lab. You just need an API key.

[Qwen Code](../../wiki/qwen-code.md#what-is-qwen-code) provides **1000 free requests per day** and works from Russia — no VPN or credit card needed.

> [!NOTE]
> If you already have a Qwen Code API key from a previous lab, use the same one. Set it as `QWEN_CODE_API_KEY` in `.env.docker.secret` (step 1.2).

If you need a new key, follow the [Qwen Code API setup guide](../../wiki/qwen-code-api.md#get-an-api-key).

Verify the API works:

```terminal
curl -s http://localhost:42002/utils/llm-api/models -H "Authorization: Bearer YOUR_QWEN_CODE_API_KEY" | head -c 100
```

You should see a JSON response with model information.

<details><summary><b>Alternative: OpenRouter (click to open)</b></summary>

If you prefer [OpenRouter](https://openrouter.ai), register and get an API key. Then in `.env.docker.secret`:

```text
LLM_API_KEY=your-openrouter-key
LLM_API_BASE_URL=https://openrouter.ai/api/v1
LLM_API_MODEL=meta-llama/llama-3.3-70b-instruct:free
```

</details>

### 1.10. Coding agent

> [!NOTE]
> You should already have a coding agent from previous labs.
> If not, [set one up](../../wiki/coding-agents.md#choose-and-use-a-coding-agent).

In this lab, you will use the coding agent (Qwen Code) to help implement tasks. The agent is your development partner — but **make sure you understand what it builds**. Each task has checkpoints where you must verify the results manually.

----

You're all set. Now go to the [tasks](../../README.md#tasks).
