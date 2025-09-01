import React from "react";
import dynamic from "next/dynamic";

// Load the client component dynamically to avoid SSR mismatches
const Demo = dynamic(() => import("../components/Demo"), { ssr: false });

export default function Page() {
  return <Demo />;
}
