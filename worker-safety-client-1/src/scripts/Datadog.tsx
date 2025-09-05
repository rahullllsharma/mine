import Script from "next/script";
import { buildRumConfig } from "@/utils/monitoring/config";
import { config } from "@/config";

export default function DatadogRUM(): JSX.Element {
  return (
    <Script
      id="datadog-rum"
      dangerouslySetInnerHTML={{
        __html: `(function(h,o,u,n,d) {
          h=h[d]=h[d]||{q:[],onReady:function(c){h.q.push(c)}}
          d=o.createElement(u);d.async=1;d.src=n
          n=o.getElementsByTagName(u)[0];n.parentNode.insertBefore(d,n)
        })(window,document,'script','https://www.datadoghq-browser-agent.com/datadog-rum-v4.js','DD_RUM')
          window.DD_RUM.onReady(function() {
            window.DD_RUM.init(${JSON.stringify(
              Object.assign({}, buildRumConfig(config))
            )});
            DD_RUM.startSessionReplayRecording();
          })`,
      }}
    />
  );
}
