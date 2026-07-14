#!/usr/bin/env python3
"""Live end-to-end smoke test for the Docker-hosted backend.

Flow:
1. Login with an existing account, or register it if it does not exist.
2. Upload a document file.
3. Create a document record, which queues processing.
4. Poll document status until it completes or fails.
5. Call retrieval with a question.

This script uses only the Python standard library so it can run directly
against a live localhost Docker deployment.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import time
import uuid
from datetime import date
from pathlib import Path
from typing import Any
from urllib import error, parse, request


DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_USERNAME = "live_test_user"
DEFAULT_EMAIL = "live_test_user@example.com"
DEFAULT_PASSWORD = "LawAssistant123!"
DEFAULT_FILE = "data/nhom_luat_giao_thong/37_2018_TT-BGTVT.docx"
DEFAULT_QUERY = "Van ban nay quy dinh noi dung gi?"


class ApiError(RuntimeError):
    def __init__(self, status: int, message: str, payload: Any | None = None):
        super().__init__(f"HTTP {status}: {message}")
        self.status = status
        self.payload = payload


def build_url(base_url: str, path: str, query: dict[str, Any] | None = None) -> str:
    url = base_url.rstrip("/") + path
    if query:
        url += "?" + parse.urlencode(query)
    return url


def read_json_response(response) -> Any:
    raw = response.read().decode("utf-8")
    if not raw:
        return None
    return json.loads(raw)


def api_request(
    base_url: str,
    method: str,
    path: str,
    *,
    token: str | None = None,
    json_body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    query: dict[str, Any] | None = None,
    timeout: int = 60,
) -> Any:
    req_headers = {"Accept": "application/json"}
    if headers:
        req_headers.update(headers)
    if token:
        req_headers["Authorization"] = f"Bearer {token}"

    data = None
    if json_body is not None:
        data = json.dumps(json_body).encode("utf-8")
        req_headers["Content-Type"] = "application/json"

    req = request.Request(
        build_url(base_url, path, query=query),
        data=data,
        headers=req_headers,
        method=method,
    )

    try:
        with request.urlopen(req, timeout=timeout) as response:
            return read_json_response(response)
    except error.HTTPError as exc:
        payload = read_json_response(exc)
        message = payload.get("message") if isinstance(payload, dict) else exc.reason
        raise ApiError(exc.code, message or str(exc), payload) from exc


def multipart_upload(
    base_url: str,
    path: str,
    file_path: Path,
    *,
    token: str,
    timeout: int = 300,
) -> Any:
    boundary = f"----LawAssistantBoundary{uuid.uuid4().hex}"
    content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    file_bytes = file_path.read_bytes()

    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(
        (
            f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"\r\n'
            f"Content-Type: {content_type}\r\n\r\n"
        ).encode("utf-8")
    )
    body.extend(file_bytes)
    body.extend(f"\r\n--{boundary}--\r\n".encode("utf-8"))

    req = request.Request(
        build_url(base_url, path),
        data=bytes(body),
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=timeout) as response:
            return read_json_response(response)
    except error.HTTPError as exc:
        payload = read_json_response(exc)
        message = payload.get("message") if isinstance(payload, dict) else exc.reason
        raise ApiError(exc.code, message or str(exc), payload) from exc


def unwrap_data(payload: Any) -> Any:
    if isinstance(payload, dict) and "data" in payload:
        return payload["data"]
    return payload


def extract_object_id(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        if "$oid" in value:
            return str(value["$oid"])
        if "oid" in value:
            return str(value["oid"])
    raise ValueError(f"Unsupported object id payload: {value!r}")


def extract_user_id(user_payload: dict[str, Any]) -> str:
    if "id" in user_payload:
        return str(user_payload["id"])
    if "_id" in user_payload:
        return extract_object_id(user_payload["_id"])
    raise ValueError(f"Unsupported user payload: {user_payload!r}")


def login(base_url: str, username: str, password: str) -> dict[str, Any]:
    payload = api_request(
        base_url,
        "POST",
        "/api/auth/login",
        json_body={"username": username, "password": password},
    )
    return unwrap_data(payload)


def register(base_url: str, username: str, email: str, password: str) -> dict[str, Any]:
    payload = api_request(
        base_url,
        "POST",
        "/api/auth/register",
        json_body={"username": username, "email": email, "password": password},
    )
    return unwrap_data(payload)


def ensure_account(base_url: str, username: str, email: str, password: str) -> dict[str, Any]:
    try:
        print(f"[auth] logging in as {username}")
        return login(base_url, username, password)
    except ApiError as exc:
        if exc.status != 401:
            raise

    print(f"[auth] account missing or password not recognized, registering {username}")
    try:
        return register(base_url, username, email, password)
    except ApiError as exc:
        if exc.status != 409:
            raise
        print("[auth] register conflicted, retrying login")
        return login(base_url, username, password)


def get_current_user(base_url: str, token: str) -> dict[str, Any]:
    payload = api_request(base_url, "GET", "/api/users/me", token=token)
    return unwrap_data(payload)


def upload_document_file(base_url: str, token: str, file_path: Path) -> dict[str, Any]:
    payload = multipart_upload(base_url, "/api/upload-files/upload", file_path, token=token)
    return unwrap_data(payload)


def create_document(
    base_url: str,
    token: str,
    *,
    so_hieu: str,
    title: str,
    effective_date: str,
    file_id: str,
) -> dict[str, Any]:
    payload = api_request(
        base_url,
        "POST",
        "/api/documents/",
        token=token,
        json_body={
            "so_hieu": so_hieu,
            "title": title,
            "effective_date": effective_date,
            "file_ids": [file_id],
        },
        timeout=120,
    )
    return unwrap_data(payload)


def get_document(base_url: str, token: str, document_id: str) -> dict[str, Any]:
    payload = api_request(base_url, "GET", f"/api/documents/{document_id}", token=token)
    return unwrap_data(payload)


def get_document_by_so_hieu(base_url: str, token: str, so_hieu: str) -> dict[str, Any] | None:
    try:
        payload = api_request(base_url, "GET", f"/api/documents/by-so-hieu/{so_hieu}", token=token)
        return unwrap_data(payload)
    except ApiError as exc:
        if exc.status == 404:
            return None
        raise


def run_retrieval(base_url: str, token: str, query_text: str) -> dict[str, Any]:
    payload = api_request(
        base_url,
        "POST",
        "/api/retrieval/search",
        token=token,
        json_body={
            "query": query_text,
            "top_k": 5,
            "use_query_preprocessing": False,
            "use_graph_retrieval": False,
            "use_semantic_retrieval": False,
            "use_dpr": False,
            "k_hops": 2,
        },
        timeout=300,
    )
    return unwrap_data(payload)


def poll_document_completion(
    base_url: str,
    token: str,
    document_id: str,
    *,
    timeout_seconds: int,
    poll_interval_seconds: int,
) -> dict[str, Any]:
    deadline = time.time() + timeout_seconds

    while True:
        document = get_document(base_url, token, document_id)
        status = document.get("status", "unknown")
        error_message = document.get("error")
        print(f"[document] status={status}")

        if status == "completed":
            return document
        if status == "failed":
            raise RuntimeError(f"Document processing failed: {error_message or 'unknown error'}")
        if time.time() >= deadline:
            raise TimeoutError(
                "Timed out waiting for document processing. "
                "If status stayed queued/processing, ensure the Docker worker is running "
                "with `docker compose --profile worker up -d`."
            )
        time.sleep(poll_interval_seconds)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a live backend flow against localhost Docker services.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--username", default=DEFAULT_USERNAME)
    parser.add_argument("--email", default=DEFAULT_EMAIL)
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    parser.add_argument("--file", default=DEFAULT_FILE, help="Path to a PDF/DOC/DOCX file to upload.")
    parser.add_argument("--query", default=DEFAULT_QUERY, help="Retrieval question to ask after processing.")
    parser.add_argument("--effective-date", default=str(date.today()))
    parser.add_argument("--timeout", type=int, default=900, help="Processing wait timeout in seconds.")
    parser.add_argument("--poll-interval", type=int, default=10, help="Polling interval in seconds.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Input file not found: {file_path}", file=sys.stderr)
        return 2

    try:
        auth_data = ensure_account(args.base_url, args.username, args.email, args.password)
        tokens = auth_data["tokens"]
        access_token = tokens["access_token"]

        user = get_current_user(args.base_url, access_token)
        print(f"[auth] authenticated as id={extract_user_id(user)} username={user['username']}")

        so_hieu = f"LIVE-TEST-{file_path.stem}"
        title = f"Live Test {file_path.stem}"
        existing_document = get_document_by_so_hieu(args.base_url, access_token, so_hieu)

        if existing_document and existing_document.get("status") == "completed":
            document_id = extract_object_id(existing_document.get("_id") or existing_document.get("id"))
            completed = existing_document
            print(f"[document] reusing completed so_hieu={so_hieu} document_id={document_id}")
        else:
            if existing_document:
                document_id = extract_object_id(existing_document.get("_id") or existing_document.get("id"))
                print(
                    f"[document] reusing in-progress so_hieu={so_hieu} "
                    f"document_id={document_id} status={existing_document.get('status')}"
                )
            else:
                print(f"[upload] uploading {file_path}")
                uploaded = upload_document_file(args.base_url, access_token, file_path)
                file_id = extract_object_id(uploaded["_id"])
                print(f"[upload] file_id={file_id} status={uploaded.get('status')}")

                print(f"[document] creating so_hieu={so_hieu}")
                created = create_document(
                    args.base_url,
                    access_token,
                    so_hieu=so_hieu,
                    title=title,
                    effective_date=args.effective_date,
                    file_id=file_id,
                )
                document_id = created["document_id"]
                print(
                    f"[document] document_id={document_id} "
                    f"task_id={created.get('task_id')} status={created.get('status')}"
                )

            completed = poll_document_completion(
                args.base_url,
                access_token,
                document_id,
                timeout_seconds=args.timeout,
                poll_interval_seconds=args.poll_interval,
            )
            print(
                "[document] completed "
                f"processed_sentences={completed.get('processed_sentences')} "
                f"extracted_triplets={completed.get('extracted_triplets')}"
            )

        print(f"[retrieval] querying: {args.query}")
        retrieval = run_retrieval(args.base_url, access_token, args.query)
        results = retrieval.get("results", [])
        print(
            "[retrieval] success "
            f"semantic_index_available={retrieval.get('semantic_index_available')} "
            f"results={len(results)}"
        )
        if results:
            print("[retrieval] first result:")
            print(json.dumps(results[0], ensure_ascii=False, indent=2))

        return 0
    except (ApiError, TimeoutError, RuntimeError, ValueError) as exc:
        print(f"Live test failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
