import type { Config } from "tailwindcss";
const config: Config = { content:["./app/**/*.{ts,tsx}","./components/**/*.{ts,tsx}"], theme:{extend:{colors:{ink:'#0b1220',blue:'#246bfd',cyan:'#16c1c8'}}}, plugins:[] };
export default config;
