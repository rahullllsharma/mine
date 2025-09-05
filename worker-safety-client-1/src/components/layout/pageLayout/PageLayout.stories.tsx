import type { ComponentMeta, ComponentStory } from "@storybook/react";

import PageFooter from "../pageFooter/PageFooter";
import PageHeader from "../pageHeader/PageHeader";
import PageLayout from "./PageLayout";

export default {
  title: "Layout/PageLayout",
  component: PageLayout,
  argTypes: { onPrimaryClick: { action: "clicked" } },
} as ComponentMeta<typeof PageLayout>;

const Header = () => (
  <PageHeader
    pageTitle="Page Layout - Header"
    linkText="Page header link"
    linkRoute=""
  />
);
const Footer = () => (
  <PageFooter
    primaryActionLabel="Page footer btn"
    onPrimaryClick={() => alert("page footer on click")}
  />
);

const TemplatePageLayout: ComponentStory<typeof PageLayout> = () => (
  <PageLayout header={<Header />}>
    <p>Hello! I`m the page layout content!</p>
  </PageLayout>
);

export const Default = TemplatePageLayout.bind({});

const TemplateWithScrollPageLayout: ComponentStory<typeof PageLayout> = () => (
  <div
    style={{
      margin: "-16px",
      height: "100vh",
      overflow: "hidden",
      display: "grid",
    }}
  >
    {/* by default, the root frame has some padding applied, with this we remove that. */}
    <PageLayout header={<Header />} footer={<Footer />}>
      <div
        style={{ height: "2000px" }}
        className="flex flex-col justify-between p-4"
      >
        <div>
          <p>Hello! I`m the page layout content! (scroll down!)</p>
          <p>
            Beware that the document needs to be prepared for this layout,
            otherwise, the content will NOT be scrollable
          </p>
          <code>
            .content-wrapper &#123; margin: &quot;-1rem&quot;, height:
            &quot;100vh&quot;, width: &quot;100%&quot;, overflow:
            &quot;hidden&quot;, display: &quot;grid&quot;, &#125;
          </code>
        </div>
        <p>
          (note that only the content is scrollable. Both the header and footer
          should be pinned to the screen, keep scrolling)
        </p>
        <p>YAY! you reached the bottom of the scrollable body</p>
      </div>
    </PageLayout>
  </div>
);

export const WithScrollableContent = TemplateWithScrollPageLayout.bind({});
