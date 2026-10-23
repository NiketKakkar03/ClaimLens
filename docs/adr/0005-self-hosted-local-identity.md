# Use self-hosted Keycloak for application login

The reviewer application needs demonstration accounts, attributed actions, and a login integration that teaches identity management without a third-party service subscription. Run the open-source Keycloak distribution locally and connect through OIDC. Keep claim permissions in the application and use documented setup to provision the demonstration accounts.

This adds a service to operate compared with an application-only login, but exercises an identity-provider integration without committing to a paid hosted identity product. The normal application profile includes Keycloak; heavy data, monitoring, and Kubernetes work runs through separate profiles. Provider tokens, browser sessions, logout, and permission changes require a reviewed implementation when the web release is built. Local development settings are not evidence of a production identity deployment.

Sources: [Keycloak project](https://www.keycloak.org/), [license](https://github.com/keycloak/keycloak/blob/main/LICENSE.txt), and [local Docker setup](https://www.keycloak.org/getting-started/getting-started-docker).
