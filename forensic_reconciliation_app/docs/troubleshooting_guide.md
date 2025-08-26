# Troubleshooting Guide

This guide provides solutions to common issues encountered while using the Frenly system.

## 1. General Issues

### Issue: Frenly API or Dashboard is not loading.

**Possible Causes:**

*   The Frenly API server (`frenly_api.py`) is not running.
*   The RabbitMQ server is not running.
*   The PostgreSQL database is not running or accessible.
*   Incorrect environment variables for database connection.

**Solutions:**

1.  **Verify API Server:** Ensure you have started the FastAPI application using `uvicorn`:
    ```bash
    uvicorn forensic_reconciliation_app.ai_service.frenly_api:app --host 0.0.0.0 --port 8000 --reload
    ```
2.  **Check RabbitMQ:** Ensure your RabbitMQ server is running. You can usually check its status via `sudo systemctl status rabbitmq-server` (Linux) or `brew services list` (macOS).
3.  **Check PostgreSQL:** Ensure your PostgreSQL database is running and accessible. Verify connection details (host, port, user, password, database name) in `frenly_data_storage.py` or your environment variables.
4.  **Environment Variables:** Double-check that `FRENLY_DB_NAME`, `FRENLY_DB_USER`, `FRENLY_DB_PASSWORD`, `FRENLY_DB_HOST`, `FRENLY_DB_PORT` are correctly set if you are using them.

### Issue: WebSocket connection fails or real-time updates are not working.

**Possible Causes:**

*   The Frenly API server is not running or the WebSocket endpoint is not correctly exposed.
*   Firewall blocking WebSocket connections.
*   Browser issues.

**Solutions:**

1.  **Verify API Server:** Ensure the FastAPI application is running and accessible.
2.  **Check Browser Console:** Open your browser's developer console (F12) and check the "Console" and "Network" tabs for WebSocket connection errors.
3.  **Firewall:** Temporarily disable your firewall to check if it's blocking the connection. If it works, configure your firewall to allow connections on port 8000 (or your chosen port).

## 2. Agent and Workflow Issues

### Issue: Agents are not showing as active or are marked as failed.

**Possible Causes:**

*   The `FrenlyMetaAgent` is not running or not properly initialized.
*   The heartbeat monitoring is not active.
*   Individual agents are genuinely failing (e.g., due to errors in their `health_check` method).

**Solutions:**

1.  **Check `FrenlyMetaAgent` Logs:** Review the logs of the `FrenlyMetaAgent` for any errors or warnings related to agent health checks.
2.  **Restart Failed Agents:** Use the "Restart All Failed Agents" button on the dashboard or the API endpoint `/api/frenly/agents/restart-all-failed` to attempt restarting them.
3.  **Inspect Individual Agent Logs:** If an agent consistently fails, check its specific logs for detailed error messages.

### Issue: Workflows are not starting or getting stuck.

**Possible Causes:**

*   Workflow definition errors in `frenly_meta_agent.py`.
*   Agents required by workflow steps are not registered or are failing.
*   Asynchronous execution issues.

**Solutions:**

1.  **Check `FrenlyMetaAgent` Logs:** Look for messages related to workflow execution, especially errors during step execution.
2.  **Verify Agent Availability:** Ensure all agents specified in the workflow steps are registered and active.
3.  **Simulate Agent Execution:** If an agent is not available, you might need to mock its behavior or ensure it's running for the workflow to proceed.

## 3. Data and Storage Issues

### Issue: Data is not being stored in the PostgreSQL database.

**Possible Causes:**

*   Database connection issues (credentials, host, port).
*   Table `reconciled_forensic_data` does not exist or has incorrect schema.
*   Errors during data insertion (e.g., data validation failures).

**Solutions:**

1.  **Verify Database Connection:** Check `FrenlyDataStorage` logs for connection errors. Manually try connecting to the database using `psql` or a GUI tool.
2.  **Check Table Schema:** Ensure the `reconciled_forensic_data` table exists and its schema matches what `FrenlyDataStorage` expects.
3.  **Review Consumer Logs:** Check `frenly_data_stream_consumer.py` logs for errors during data validation, cleansing, or insertion.

## 4. Performance Issues

### Issue: System is slow or unresponsive.

**Possible Causes:**

*   High message volume overwhelming the consumer.
*   Inefficient data processing logic.
*   Database bottlenecks.
*   Insufficient system resources (CPU, memory).

**Solutions:**

1.  **Monitor Metrics:** Use the "Performance Metrics" section on the dashboard or the `/api/frenly/metrics` endpoint to identify bottlenecks (e.g., high response times, high failed commands).
2.  **Adjust Batch Size:** Experiment with the `batch_size` and `batch_timeout` in `frenly_data_stream_consumer.py` to optimize throughput.
3.  **Optimize Database Queries:** Analyze database query performance. Ensure indexes are used effectively.
4.  **Scale Resources:** If running on a server, consider increasing CPU, memory, or disk I/O.

## 5. Logging and Monitoring

### Issue: Logs are not providing enough information or are too verbose.

**Possible Causes:**

*   Incorrect logging levels configured.
*   Missing log statements in critical sections.

**Solutions:**

1.  **Adjust Logging Level:** Modify `logging.basicConfig(level=logging.INFO)` to `DEBUG` for more verbose output during development, or `WARNING`/`ERROR` for production.
2.  **Add More Log Statements:** Identify areas where more context is needed and add appropriate `logger.info()`, `logger.debug()`, `logger.warning()`, `logger.error()`, or `logger.critical()` calls.
