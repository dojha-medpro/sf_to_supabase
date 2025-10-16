# CloudMailin Setup Guide

## Overview
This guide shows you how to configure CloudMailin to automatically process Salesforce CSV exports sent via email and load them into Supabase.

## Architecture
```
Salesforce Report Email → CloudMailin → Your Flask Webhook → ETL Pipeline → Supabase
```

## Step 1: Get Your Webhook URL

Your CloudMailin webhook endpoint is:
```
https://[YOUR-REPLIT-DOMAIN]/webhook/cloudmailin
```

To find your Replit domain:
1. Click the "Webview" button in Replit
2. Copy the URL from your browser (e.g., `https://abc123xyz.replit.app`)
3. Your webhook URL will be: `https://abc123xyz.replit.app/webhook/cloudmailin`

## Step 2: Create CloudMailin Account

1. Go to [cloudmailin.com](https://www.cloudmailin.com/)
2. Sign up for a free account
3. Click "Create New Address" in the dashboard

## Step 3: Configure Webhook Security (REQUIRED)

**⚠️ Security First!** The webhook requires authentication to prevent unauthorized access.

1. **Generate a secure webhook token**:
   ```bash
   # Generate a random token (use any method)
   openssl rand -hex 32
   # Example output: a1b2c3d4e5f6...
   ```

2. **Add token to Replit Secrets**:
   - In Replit, click "Tools" → "Secrets"
   - Add new secret:
     - Key: `CLOUDMAILIN_WEBHOOK_TOKEN`
     - Value: `[your-generated-token]`
   - Click "Add Secret"

3. **Restart your Flask app** to load the new environment variable

## Step 4: Configure CloudMailin Address

### Basic Settings:
1. **Email Address**: Choose your custom CloudMailin email (e.g., `salesforce@yourdomain.cloudmailin.net`)
2. **Target URL**: Paste your webhook URL: `https://[YOUR-REPLIT-DOMAIN]/webhook/cloudmailin`
3. **HTTP Format**: Select **"JSON (Normalized)"**
4. **HTTP Method**: POST
5. **Status**: Enabled

### Security Settings (REQUIRED):
6. **Custom HTTP Headers**:
   - Click "Add Custom Header"
   - Header Name: `X-CloudMailin-Token`
   - Header Value: `[your-generated-token]` (same as CLOUDMAILIN_WEBHOOK_TOKEN)
   - This authenticates CloudMailin's requests to your webhook

### Attachment Settings (Recommended):
For large CSV files, configure cloud storage to avoid payload size limits:

1. **Cloud Storage** (Optional but recommended):
   - Go to Settings → Attachment Storage
   - Configure S3, Azure, Google Cloud, or S3-compatible storage
   - CloudMailin will upload attachments and send URLs instead of base64

2. **Size Limits**: 
   - Without storage: ~10MB max (base64 encoded)
   - With storage: Unlimited (URLs provided)

## Step 5: Configure Salesforce Email Reports

### Option A: Manual Daily Emails
1. In Salesforce, schedule reports to email to your CloudMailin address
2. Ensure CSV exports are attached to the emails

### Option B: Automated Daily Emails
1. Set up Salesforce scheduled reports
2. Add your CloudMailin email to the recipient list
3. Choose "CSV" as the export format
4. Set schedule (e.g., daily at 6 AM)

## Step 6: CSV Filename Patterns

The system auto-detects which mapping to use based on filename patterns:

| Filename Contains | Mapping Used | Target Table |
|-------------------|--------------|--------------|
| `contact` or `candidate` | contacts.yaml | staging.contacts |
| `form_submission` | form_submission.yaml | staging.form_submission |
| `job_applicant_history` | job_applicant_history_events.yaml | staging.job_applicant_history |
| `job_applicant` | job_applicants.yaml | staging.job_applicant |
| `contacts_with_jobs` | contacts_with_jobs_joined.yaml | staging.contacts_with_jobs |
| `jobs_and_placement` | jobs_and_placement.yaml | staging.jobs_and_placements |
| `placement_history` | placement_history_events.yaml | staging.placement_history |

**Important**: Name your CSV files appropriately so the system can auto-detect the correct mapping.

### Example Filenames:
- ✅ `contacts_export_2025_10_16.csv` → Uses contacts.yaml
- ✅ `job_applicant_report_daily.csv` → Uses job_applicants.yaml
- ✅ `form_submission_data.csv` → Uses form_submission.yaml
- ❌ `data.csv` → Will be skipped (no matching pattern)

## Step 7: Test the Integration

### Test Email:
1. Send a test email to your CloudMailin address with a CSV attachment
2. Check the Load History page in your app to verify processing
3. Check Supabase to confirm data was loaded

### Example Test Email:
```
To: salesforce@yourdomain.cloudmailin.net
Subject: Test - Salesforce Daily Report
Attachment: contacts_test.csv
```

### Monitor Results:
1. **In Replit**: Check console logs for real-time processing
2. **In App**: Go to `/history` to see load status
3. **In Supabase**: Query staging tables to verify data

## Step 8: Troubleshooting

### Webhook Not Receiving Data
- Verify webhook URL is correct in CloudMailin settings
- Ensure Replit app is running (workflows should be active)
- Check CloudMailin delivery logs for errors

### File Not Processing
- Check filename contains a matching pattern (see table above)
- Verify CSV format matches the expected mapping
- Review quarantined files in `/quarantine` folder

### QA Validation Failures
- Check validation errors in Load History
- Review the mapping YAML for required fields
- Verify CSV headers match expected format

## CloudMailin Response Format

The webhook returns a JSON response:

### Success Example:
```json
{
  "status": "ok",
  "email_from": "salesforce@example.com",
  "email_subject": "Daily Report Export",
  "processed_files": [
    {
      "file": "contacts_10_16_2025.csv",
      "status": "success",
      "load_id": 123,
      "rows_loaded": 50000,
      "target_table": "staging.contacts"
    }
  ]
}
```

### Error Example:
```json
{
  "status": "ok",
  "email_from": "salesforce@example.com",
  "email_subject": "Daily Report Export",
  "processed_files": [
    {
      "file": "unknown_report.csv",
      "status": "skipped",
      "reason": "No matching mapping pattern"
    }
  ]
}
```

## Email Notifications (Future Enhancement)

To enable email notifications for success/failure:

1. Configure SMTP settings in environment variables:
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

2. Or use SendGrid/Mailgun API with API key

The notification service is already in place - just needs SMTP configuration.

## Security Features (Built-in)

### ✅ Webhook Authentication (REQUIRED)
The webhook is protected with token-based authentication:
- Rejects requests without valid `X-CloudMailin-Token` header
- Token must match `CLOUDMAILIN_WEBHOOK_TOKEN` environment variable
- **IMPORTANT**: Always configure this token (see Step 3 above)

### ✅ Attachment URL Validation
When CloudMailin uses cloud storage (S3, Azure, etc.):
- Only downloads from whitelisted domains:
  - AWS S3 (`s3.amazonaws.com`)
  - Google Cloud Storage (`storage.googleapis.com`)
  - Azure Blob Storage (`blob.core.windows.net`)
  - CloudMailin CDN (`cloudmailin.com`)
  - Digital Ocean Spaces, Cloudflare R2
- Prevents SSRF attacks from malicious URLs

### ✅ Size & Timeout Limits
- Maximum attachment size: 100 MB
- Download timeout: 30 seconds
- Prevents denial-of-service attacks

### Additional Security (Optional)

#### IP Whitelist
Configure CloudMailin to only accept emails from specific sender IPs (e.g., Salesforce IPs).

#### Email Sender Validation
Add custom validation in the webhook to verify sender email domains:
```python
allowed_senders = ['@salesforce.com', '@mycompany.com']
if not any(sender_domain in from_email for sender_domain in allowed_senders):
    return jsonify({'status': 'error', 'message': 'Unauthorized sender'}), 403
```

## Support & Resources

- **CloudMailin Docs**: https://docs.cloudmailin.com/
- **CloudMailin Dashboard**: https://www.cloudmailin.com/addresses
- **Replit App History**: `/history` endpoint
- **Notification Logs**: `etl_notifications.log`

## Daily Workflow Summary

Once configured:
1. ✅ Salesforce sends scheduled report email → CloudMailin
2. ✅ CloudMailin receives email → Extracts CSV attachments
3. ✅ CloudMailin POSTs to webhook → Flask app receives JSON
4. ✅ Auto-detect mapping from filename → Route to correct pipeline
5. ✅ QA validation → Transform → Load to Supabase
6. ✅ Success/failure logged → Check `/history` for results

**Zero manual intervention required!** 🎉
