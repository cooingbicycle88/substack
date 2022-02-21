## Containerized Dashboard and API

Associated with post:

[substack - Containerizing Dashboards and Custom API's](https://schoolofdata.substack.com/p/containerizing-dashboards-and-custom)

#### docker-compose.yml

```
  version: "3"
  services:
    substackapi:
      build: "./api"
      ports:
        - "7000:7000"
    substackdashboard:
      build: ./dashboard
      ports:
        - "8502:8502"
      environment:
        - API_HOST=http://substackapi:7000
      depends_on: 
        - substackapi 
```
