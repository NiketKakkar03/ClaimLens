import Keycloak from 'keycloak-js'

export const keycloak = new Keycloak({
  url: import.meta.env.VITE_OIDC_URL ?? 'http://localhost:8180',
  realm: import.meta.env.VITE_OIDC_REALM ?? 'claims-local',
  clientId: import.meta.env.VITE_OIDC_CLIENT_ID ?? 'claims-reviewer',
})

export async function accessToken(): Promise<string> {
  await keycloak.updateToken(30)
  if (!keycloak.token) throw new Error('The login session has expired')
  return keycloak.token
}
