
## 5. Configuration Requirements (Outside Sandbox)

Deploying the SEBA website outside the development sandbox requires specific configurations to ensure it runs reliably, securely, and connects correctly to the backend API.

### 5.1 Environment Variables

Environment variables are crucial for managing configuration settings that differ between development and production environments without hardcoding them into the source code.

**Key Variables Needed:**

1.  **`API_BASE_URL` (or similar)**: This is the most critical variable. It must point to the **publicly accessible URL** of your deployed SEBA backend API. In the sandbox, this might have been a local or internal URL, but for a live deployment, it needs to be the production API endpoint (e.g., `https://api.yourdomain.com/v1`).
2.  **`AUTH_DOMAIN` / `AUTH_CLIENT_ID` (If using external Auth)**: If you integrate a third-party authentication provider like Auth0 or Okta, you will need to configure their specific domain and client ID variables.
3.  **`GA_TRACKING_ID` / `OTHER_ANALYTICS_IDS` (Optional)**: For tracking website usage with services like Google Analytics, Hotjar, etc.

**Implementation:**

-   Your JavaScript code (specifically `api.js` or a dedicated config file) needs to read these variables. Since this is a static site without a Node.js runtime during build (unless you add a build tool), injecting environment variables can be tricky.
    -   **Option 1 (Build Tool)**: If using Webpack/Vite/Parcel, you can use plugins (like `webpack.DefinePlugin` or Vite's built-in env handling) to replace placeholders (e.g., `process.env.API_BASE_URL`) with actual values during the build process.
    -   **Option 2 (Runtime Configuration)**: Load a configuration file (`config.js`) that defines these variables. This file could be generated dynamically during deployment or manually created.
        ```javascript
        // Example: config.js
        window.SEBA_CONFIG = {
            API_BASE_URL: 'https://api.yourdomain.com/v1'
        };
        ```
        ```html
        <!-- Load config before other scripts -->
        <script src="config.js"></script>
        <script src="js/api.js"></script>
        ```
        ```javascript
        // In api.js
        const SEBA_API = {
            baseURL: window.SEBA_CONFIG.API_BASE_URL || 'http://localhost:5000/api', // Default fallback
            // ...
        };
        ```
    -   **Option 3 (Platform Injection)**: Some platforms (like Netlify) allow injecting snippets or environment variables directly into the HTML during build/deploy, but this is less common for simple static sites.

**Setting Variables on Platforms:**

-   **Netlify**: Go to `Site settings` > `Build & deploy` > `Environment`. Add your variables (e.g., `API_BASE_URL = https://api.yourdomain.com/v1`). You might need to trigger a rebuild.
-   **Vercel**: Go to `Project Settings` > `Environment Variables`. Add your variables.
-   **Custom Server**: Set system environment variables or use a `.env` file loaded by your server process (if you add a backend component) or build script.

### 5.2 Build Script Adjustments for Production

As mentioned in Section 3, the current `npm run build` script is basic. For production, you should enhance it:

1.  **Integrate a Build Tool**: Add Webpack, Parcel, or Vite.
2.  **Configure Production Mode**: Ensure the build tool runs in `production` mode to enable optimizations like minification, tree shaking, etc.
3.  **Update `package.json`**: Modify the `build` script to invoke the build tool (e.g., `"build": "webpack --mode production"`).

### 5.3 SSL/HTTPS Configuration

Running the site over HTTPS is **essential** for security, especially since it handles authentication tokens.

-   **Netlify/Vercel/Cloudflare Pages/GitHub Pages**: These platforms provide **free, automatic SSL certificates** (usually via Let's Encrypt) and enable HTTPS by default for both their subdomains and custom domains. You typically just need to ensure HTTPS is enforced in the settings.
-   **AWS Amplify**: Also provides managed SSL certificates.
-   **Custom Server (Nginx/Apache)**: You are responsible for obtaining and configuring SSL certificates.
    -   **Obtain Certificate**: Use Let's Encrypt (via tools like Certbot) for free certificates or purchase one from a Certificate Authority.
    -   **Configure Web Server**: Update your Nginx or Apache configuration to listen on port 443, specify the certificate and key file paths, and enable SSL protocols (TLS 1.2+ recommended).
    -   **Redirect HTTP to HTTPS**: Set up a permanent (301) redirect for all HTTP traffic to HTTPS.
    -   **HSTS Header**: Consider adding the `Strict-Transport-Security` header to enforce HTTPS.

### 5.4 Custom Domain Configuration

To use your own domain (e.g., `app.seba-analysis.com`) instead of the platform's default subdomain:

1.  **Purchase Domain**: Buy a domain name from a registrar (Google Domains, Namecheap, etc.).
2.  **Add Domain to Platform**: In your hosting platform's dashboard (Netlify, Vercel), add your custom domain.
3.  **Configure DNS**: The platform will provide DNS records (usually CNAME or A records) that you need to add/update in your domain registrar's DNS settings. This points your domain name to the hosting platform's servers.
    -   Example (Netlify): You might point `www.yourdomain.com` via CNAME to `yoursite.netlify.app` and the root domain (`yourdomain.com`) via an A record to Netlify's load balancer IP.
4.  **Propagation**: Wait for DNS changes to propagate globally (can take minutes to 48 hours).
5.  **Verify & Enable HTTPS**: Once DNS propagates, the platform should verify the domain and automatically provision an SSL certificate for it.

### 5.5 CORS (Cross-Origin Resource Sharing)

Since your frontend website (e.g., `https://app.seba-analysis.com`) will be making requests to your backend API (e.g., `https://api.seba-analysis.com`) hosted on a different domain, the **backend API server must be configured to handle CORS**.

-   The API server needs to send back appropriate CORS headers, specifically `Access-Control-Allow-Origin`, indicating that requests from your frontend domain are permitted.
    -   Example Header: `Access-Control-Allow-Origin: https://app.seba-analysis.com`
-   It also needs to handle preflight `OPTIONS` requests for complex requests (like those with `Authorization` headers or non-standard methods/headers).
-   Failure to configure CORS correctly on the **backend** will result in browsers blocking frontend API requests due to security restrictions.

### 5.6 API Endpoint URL

Ensure the `API_BASE_URL` configured in your frontend points to the correct, publicly accessible production URL of your deployed backend API. Any mismatch will prevent the website from fetching data.



## 6. Step-by-Step Summary: Create, API-Enable, Deploy, Run

Here are the exact steps to take the SEBA website project from its current state (as developed in the sandbox) to a fully deployed and running application on your own domain outside the sandbox:

**Phase 1: Preparation & Code Enhancement**

1.  **Get the Code**: Obtain the final SEBA website source code (HTML, CSS, JS files, `package.json`, etc.) – likely from the zip file provided or a Git repository.
2.  **Set Up Local Environment**: Ensure you have Node.js and npm installed on your local machine.
3.  **Install Dependencies**: Navigate to the project directory in your terminal and run `npm install`.
4.  **(Optional but Recommended) Enhance Build Process**: Integrate a build tool like Webpack or Vite. Configure it for production builds (minification, bundling, environment variable injection, cache busting). Update the `build` script in `package.json`.
5.  **Implement Environment Variable Reading**: Modify `js/api.js` (or a new `config.js`) to read the `API_BASE_URL` from the environment (e.g., using `process.env.API_BASE_URL` if using a build tool, or `window.SEBA_CONFIG.API_BASE_URL` if using a runtime config file).

**Phase 2: Backend API Deployment**

6.  **Deploy SEBA Backend API**: Ensure the SEBA backend API (developed separately) is deployed to a publicly accessible server or platform (e.g., Heroku, AWS EC2/ECS, Google Cloud Run). Note its **production base URL** (e.g., `https://api.yourdomain.com/v1`).
7.  **Configure API CORS**: Configure the deployed backend API server to allow requests from your intended frontend domain (e.g., `https://app.yourdomain.com`) by setting the `Access-Control-Allow-Origin` header and handling `OPTIONS` requests.

**Phase 3: Frontend Deployment**

8.  **Choose Hosting Platform**: Select your preferred hosting platform (Netlify or Vercel recommended).
9.  **Create Account**: Sign up for an account on the chosen platform.
10. **Configure Environment Variables**: In the platform's dashboard, set the `API_BASE_URL` environment variable to the production URL of your deployed backend API (from step 6).
11. **Build for Production**: Run the production build command (e.g., `npm run build` or `webpack --mode production`). This generates the optimized static files in the `dist` directory.
12. **Deploy Files**: Deploy the contents of the `dist` directory to your hosting platform.
    *   **Netlify/Vercel (Git)**: Connect your Git repository, configure the build command (e.g., `npm run build`), and specify the publish directory (`dist`). The platform will build and deploy automatically on push.
    *   **Netlify/Vercel (Manual)**: Use their CLI tools (`netlify deploy --prod` or `vercel --prod`) or drag-and-drop the `dist` folder in their web UI.
13. **(Optional) Configure Custom Domain**: Purchase a domain name and configure it in your hosting platform's settings, updating DNS records at your registrar as instructed.
14. **Verify HTTPS**: Ensure HTTPS is automatically enabled and enforced by the platform for your deployed site (both the default subdomain and your custom domain, if used).

**Phase 4: Testing & Verification**

15. **Access Deployed Site**: Open your deployed website URL in a browser.
16. **Test Functionality**: Thoroughly test all features:
    *   Stock search and analysis.
    *   Chart rendering.
    *   Stock screening.
    *   Chatbot interaction.
    *   Authentication (if implemented).
    *   Responsiveness on different devices.
17. **Check API Connection**: Use browser developer tools (Network tab) to confirm that API requests are being made to the correct production `API_BASE_URL` and are succeeding (Status 2xx). Check for CORS errors in the console.
18. **Verify HTTPS**: Confirm the browser shows a secure connection (padlock icon).

By following these steps, you will have successfully created, API-enabled, deployed, and run the SEBA website on your own infrastructure outside the original sandbox environment.

