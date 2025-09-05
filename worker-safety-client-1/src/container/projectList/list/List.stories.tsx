import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { Project } from "@/types/project/Project";
import type { ListState as ListProjectUiState } from "./List";
import { useState, useEffect } from "react";
import { useProjects } from "@/hooks/useProjects";

import { WrapperScroll } from "@/utils/dev/storybook";
import { List as ProjectsList } from "./List";

export default {
  title: "Container/ProjectsList/List",
  component: ProjectsList,

  decorators: [
    Story => (
      <WrapperScroll>
        <Story />
      </WrapperScroll>
    ),
  ],
} as ComponentMeta<typeof ProjectsList>;

const Template: ComponentStory<typeof ProjectsList> = args => {
  const projects = useProjects();

  return <ProjectsList {...args} projects={projects} onLoadMore={undefined} />;
};

export const Playground = Template.bind({});

const InfiniteScrollTemplate: ComponentStory<typeof ProjectsList> = args => {
  // eslint-disable-next-line react-hooks/rules-of-hooks
  const makeData = () => new Array(5).fill(useProjects()).flat();

  const max = 30;
  const [data, setData] = useState<Project[]>([]);
  const [uiState, setUiState] = useState<ListProjectUiState>();

  const onLoadMore = () => {
    // with fake delay
    setUiState("loading");
    return new Promise(resolve => {
      return setTimeout(() => {
        if (data.length < max) {
          setUiState(undefined);
          return resolve(setData(d => d.concat(makeData())));
        }

        resolve(data);
        setUiState("complete");
      }, 1500);
    });
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      setUiState(undefined);
      setData(makeData());
    }, 1500);

    return () => {
      clearTimeout(timer);
    };
  }, []);

  return (
    <ProjectsList
      {...args}
      projects={data}
      state={uiState}
      onLoadMore={onLoadMore}
    />
  );
};

export const withInfiniteScroll = InfiniteScrollTemplate.bind({});
