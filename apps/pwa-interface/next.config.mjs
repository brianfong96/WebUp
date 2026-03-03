import withPWA from "next-pwa";

const isDev = process.env.NODE_ENV !== "production";

export default withPWA({
  dest: "public",
  disable: isDev,
  register: true,
  skipWaiting: true
})({
  typedRoutes: true,
  experimental: {
    externalDir: true
  }
});
