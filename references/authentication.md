# Authentication

The Qapla' public API v1.3 uses a **per-channel private API Key**. There is no
OAuth/JWT in v1.x — authentication is stateless, one key per request.

## Where the key comes from

The merchant finds the private API Key in the Qapla' Control Panel
(<https://cp.qapla.it>):

```
Settings > Channels > [CHANNEL_NAME] > "Configure" > Channel > Private API Key
```

Each **channel** (store/marketplace) has its own key. A call authenticated with
a given key operates only on that channel's data. A merchant with multiple
channels has multiple keys.

## How to send it

Put the key in the **JSON request body** under `apiKey`:

```json
{
  "apiKey": "YOUR_CHANNEL_PRIVATE_API_KEY",
  "pushShipment": [ { "...": "..." } ]
}
```

> **Exception — `getQuotes`.** This one endpoint does *not* take `apiKey` in the
> body: it expects the key in an HTTP header `x-api-key` (and `x-sandbox` for
> sandbox). See `getquotes.md`.

## Testing the key

The quickest connectivity test is the `getChannel` endpoint — call it with just
your `apiKey` and confirm `result == "OK"`.

## Security

- The key is a **secret**: it grants full read/write access to the channel.
- Never commit it, never put it in client-side code, never log it.
- Read it from environment/config at runtime.
- If leaked, rotate it from the Control Panel.
- Misuse/abuse of the API can get the key **banned** (see rate limiting in
  `conventions.md`).

> The newer API **v2** introduces a different, more secure auth model. If you are
> starting a brand-new integration, check whether v2 is appropriate at
> <https://api.qapla.dev/v2>. This skill covers v1.3.
