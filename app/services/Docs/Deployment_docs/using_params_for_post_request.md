Yes, you've correctly identified that query parameters in `httpx` (as in `requests`) require specific handling, especially when passing them with a `POST` request. The issue arises because the query parameters need to be explicitly separated from the URL, rather than appended manually.

In `httpx`, you can use the `params` argument to add query parameters to your request in a structured way, rather than embedding them directly in the URL string. This way, `httpx` takes care of encoding the parameters correctly, avoiding potential issues with special characters and ensuring that they’re handled as expected on the receiving end.

Here's how to adjust your code using `httpx`:

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://database.kundalin.com/ingest/",
        params={"index_name": index_name},  # Using params for query parameters
        json=data_list
    )
```

### Explanation

- **`params={"index_name": index_name}`**: This sends `index_name` as a query parameter in the `POST` request.
- **`json=data_list`**: This sets the body of the request to `data_list`, assuming `data_list` is the JSON payload you're sending.

This approach is generally more reliable, as it avoids potential encoding issues and ensures that the query parameters are passed as intended. By structuring the request this way, FastAPI will correctly interpret `index_name` as a query parameter, which should help resolve the `422 Unprocessable Entity` error you're encountering.