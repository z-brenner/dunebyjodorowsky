/* Static assets on Workers answer a byte-range request with the whole file, and Safari will not
   play a video without ranges. This Worker runs for /film/* only: it reads the file from the
   assets and returns just the bytes asked for. Everything else is served by the assets as before. */
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const range = request.headers.get("Range");
    const film = url.pathname.startsWith("/film/") && (request.method === "GET" || request.method === "HEAD");
    if (!film) return env.ASSETS.fetch(request);

    const headers = new Headers(request.headers);
    headers.delete("Range"); headers.delete("If-Range");
    const full = await env.ASSETS.fetch(new Request(request.url, { method: "GET", headers }));
    const out = new Headers(full.headers);
    if (full.status === 200) out.set("Accept-Ranges", "bytes");
    const m = range && /^bytes=(\d*)-(\d*)$/.exec(range.trim());
    /* If-Range: the client holds part of some version of the file. If that is not this version, it must get
       the whole file, or it would join pieces of two different films. Only an exact match counts. */
    const held = request.headers.get("If-Range");
    const same = !held || (held.startsWith('"') ? held === full.headers.get("ETag")
      : !held.startsWith("W/") && full.headers.has("Last-Modified") && Date.parse(held) === Date.parse(full.headers.get("Last-Modified")));
    if (full.status !== 200 || !m || !same || (m[1] === "" && m[2] === "")) {
      return new Response(request.method === "HEAD" ? null : full.body, { status: full.status, headers: out });
    }

    /* "bytes=0-" asks for everything: pass the file straight through instead of holding it in memory */
    const known = Number(full.headers.get("Content-Length"));
    if (m[1] === "0" && m[2] === "" && known > 0) {
      out.set("Content-Range", "bytes 0-" + (known - 1) + "/" + known);
      return new Response(request.method === "HEAD" ? null : full.body, { status: 206, headers: out });
    }
    const bytes = await full.arrayBuffer(), size = bytes.byteLength;
    let start, end;
    if (m[1] === "") { start = Math.max(0, size - Number(m[2])); end = size - 1; }            /* the last N bytes */
    else { start = Number(m[1]); end = m[2] === "" ? size - 1 : Math.min(Number(m[2]), size - 1); }
    out.delete("Content-Encoding");
    if (start >= size || start > end) {
      out.set("Content-Range", "bytes */" + size); out.delete("Content-Length");
      return new Response(null, { status: 416, headers: out });
    }
    out.set("Content-Range", "bytes " + start + "-" + end + "/" + size);
    out.set("Content-Length", String(end - start + 1));
    return new Response(request.method === "HEAD" ? null : bytes.slice(start, end + 1), { status: 206, headers: out });
  }
};
