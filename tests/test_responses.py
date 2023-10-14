from seastar.responses import Response, JsonResponse


class TestResponse:
    def test_response_body(self):
        resp = Response("Hello World")
        assert resp.to_result() == {"body": "Hello World"}

    def test_response_status_code(self):
        resp = Response("Hello World", status_code=200)
        assert resp.to_result() == {"body": "Hello World", "statusCode": 200}

    def test_response_headers(self):
        resp = Response("Hello World", status_code=200, headers={"foo": "bar"})
        assert resp.to_result() == {
            "body": "Hello World",
            "statusCode": 200,
            "headers": {"foo": "bar"},
        }


class TestJsonResponse:
    def test_render(self):
        content = {"hello": "world"}
        resp = JsonResponse(content)
        assert resp.body == '{"hello":"world"}'
