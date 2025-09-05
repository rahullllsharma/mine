import Link from "@/components/shared/link/Link";
import NextLink from "next/link";

interface linkProps {
  href: string;
  labelName: string;
}

const LinkComponent = ({ href, labelName }: linkProps) => {
  return (
    <NextLink href={href} passHref>
      <Link label={labelName} iconLeft="chevron_big_left" className="mb-3" />
    </NextLink>
  );
};

export default LinkComponent;
