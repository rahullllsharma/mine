import type { Project } from "@/types/project/Project";
import { useRouter } from "next/router";
import CardItem from "@/components/cardItem/CardItem";

function ProjectItems({ projects }: { projects: Project[] }) {
  const router = useRouter();

  return (
    <>
      {projects.map(project => (
        <CardItem
          project={project}
          key={project.id}
          onClick={() =>
            router.push({
              pathname: "/projects/[id]",
              query: { id: project.id },
            })
          }
        />
      ))}
    </>
  );
}

export { ProjectItems };
