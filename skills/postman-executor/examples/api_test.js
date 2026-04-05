{
  "info": {
    "name": "API Test Collection",
    "description": "Example Postman collection for API testing",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "baseUrl",
      "value": "https://jsonplaceholder.typicode.com"
    }
  ],
  "item": [
    {
      "name": "Get All Posts",
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test('Status code is 200', function() {",
              "    pm.response.to.have.status(200);",
              "});",
              "",
              "pm.test('Response has posts array', function() {",
              "    var jsonData = pm.response.json();",
              "    pm.expect(jsonData).to.be.an('array');",
              "    pm.expect(jsonData.length).to.be.above(0);",
              "});",
              "",
              "pm.test('First post has required fields', function() {",
              "    var jsonData = pm.response.json();",
              "    var firstPost = jsonData[0];",
              "    pm.expect(firstPost).to.have.property('userId');",
              "    pm.expect(firstPost).to.have.property('id');",
              "    pm.expect(firstPost).to.have.property('title');",
              "    pm.expect(firstPost).to.have.property('body');",
              "});"
            ]
          }
        }
      ],
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{baseUrl}}/posts",
          "host": ["{{baseUrl}}"],
          "path": ["posts"]
        }
      }
    },
    {
      "name": "Get Single Post",
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test('Status code is 200', function() {",
              "    pm.response.to.have.status(200);",
              "});",
              "",
              "pm.test('Response has correct id', function() {",
              "    var jsonData = pm.response.json();",
              "    pm.expect(jsonData.id).to.eql(1);",
              "});",
              "",
              "pm.test('Response has all required fields', function() {",
              "    var jsonData = pm.response.json();",
              "    pm.expect(jsonData).to.include.all.keys('userId', 'id', 'title', 'body');",
              "});"
            ]
          }
        }
      ],
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{baseUrl}}/posts/1",
          "host": ["{{baseUrl}}"],
          "path": ["posts", "1"]
        }
      }
    },
    {
      "name": "Create New Post",
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test('Status code is 201 (Created)', function() {",
              "    pm.response.to.have.status(201);",
              "});",
              "",
              "pm.test('Response has id assigned', function() {",
              "    var jsonData = pm.response.json();",
              "    pm.expect(jsonData.id).to.be.a('number');",
              "});",
              "",
              "pm.test('Response echoes title and body', function() {",
              "    var jsonData = pm.response.json();",
              "    pm.expect(jsonData.title).to.eql('Test Post Title');",
              "    pm.expect(jsonData.body).to.eql('This is a test post body');",
              "    pm.expect(jsonData.userId).to.eql(1);",
              "});"
            ]
          }
        }
      ],
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n    \"title\": \"Test Post Title\",\n    \"body\": \"This is a test post body\",\n    \"userId\": 1\n}"
        },
        "url": {
          "raw": "{{baseUrl}}/posts",
          "host": ["{{baseUrl}}"],
          "path": ["posts"]
        }
      }
    },
    {
      "name": "Update Post",
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test('Status code is 200', function() {",
              "    pm.response.to.have.status(200);",
              "});",
              "",
              "pm.test('Response confirms update', function() {",
              "    var jsonData = pm.response.json();",
              "    pm.expect(jsonData.id).to.eql(1);",
              "});"
            ]
          }
        }
      ],
      "request": {
        "method": "PUT",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n    \"id\": 1,\n    \"title\": \"Updated Title\",\n    \"body\": \"Updated body content\",\n    \"userId\": 1\n}"
        },
        "url": {
          "raw": "{{baseUrl}}/posts/1",
          "host": ["{{baseUrl}}"],
          "path": ["posts", "1"]
        }
      }
    },
    {
      "name": "Delete Post",
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test('Status code is 200', function() {",
              "    pm.response.to.have.status(200);",
              "});",
              "",
              "pm.test('Response body is empty object', function() {",
              "    var jsonData = pm.response.json();",
              "    pm.expect(jsonData).to.be.empty;
              "});"
            ]
          }
        }
      ],
      "request": {
        "method": "DELETE",
        "header": [],
        "url": {
          "raw": "{{baseUrl}}/posts/1",
          "host": ["{{baseUrl}}"],
          "path": ["posts", "1"]
        }
      }
    },
    {
      "name": "Get Comments for Post",
      "event": [
        {
          "listen": "test",
          "script": {
            "exec": [
              "pm.test('Status code is 200', function() {",
              "    pm.response.to.have.status(200);",
              "});",
              "",
              "pm.test('Comments array is not empty', function() {",
              "    var jsonData = pm.response.json();",
              "    pm.expect(jsonData).to.be.an('array');",
              "    pm.expect(jsonData.length).to.be.above(0);",
              "});",
              "",
              "pm.test('Each comment has email', function() {",
              "    var jsonData = pm.response.json();",
              "    jsonData.forEach(function(comment) {",
              "        pm.expect(comment).to.have.property('email');",
              "        pm.expect(comment.email).to.match(/.+@.+\\..+/);",
              "    });",
              "});"
            ]
          }
        }
      ],
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{baseUrl}}/posts/1/comments",
          "host": ["{{baseUrl}}"],
          "path": ["posts", "1", "comments"]
        }
      }
    }
  ]
}
