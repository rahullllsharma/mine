// TODO
// This is a temporary implementation for Updating Heca Rules Based
// on the Tenant. Once we have API ready will integrate those api in Front End
// for retreiving the Heca Rules on basis of tenant from DB
import Link from "next/link";

const HecaRulesForExelon = () => {
  return (
    <div className="px-8">
      <ol className="list-decimal list-outside text-justify space-y-2">
        <li>Only document EBO findings, for work actually observed.</li>
        <li>
          Separate tasks, require separate entries, even if performed by the
          same crew/worker.
        </li>
        <li>
          Common tasks can be bundled as a single task entry, only if all direct
          controls are shared between the tasks.
        </li>
        <li>
          Within each task, all high-energy hazards observed, shall be assessed
          separately for the presence of Direct Controls.
        </li>
        <li>
          Some Direct Controls work as a system. All components of that system
          must be in place to count as a “Success”. If any one component of the
          system is not in place, then the system shall be deemed an “Exposure”.
        </li>
        <li>
          All individuals within a task are assessed as a unit. If Direct
          Controls are applied at the individual level (ex: Fall Protection
          harness) and is properly used by all employees for that task, then
          that would count as one (1) “Success”. If any one individual Direct
          Control is not in place, then the task would include one (1)
          “Exposure”.
        </li>
        <li>
          Observers must make reasonable efforts to verify that direct controls
          are installed and used properly.
        </li>
        <li>
          A task ends, with the removal of safeguards, or the end of the shift,
          whichever comes first.{" "}
        </li>
      </ol>
    </div>
  );
};

const HecaRulesForXcelEnergy = () => {
  return (
    <div className="px-8">
      <ol className="list-decimal list-outside text-justify space-y-2">
        <li>
          HECA is based on observations of active work and not the assessment or
          classification of an incident or the review of paperwork alone.
          <sup>2</sup>
        </li>
        <li>
          Each HECA measurement must correspond to one crew performing one task
          during one working day.<sup>3</sup> Multiple crews and/or tasks
          require multiple HECA measurements.
        </li>
        <li>
          If a crew performs more than one task during the observation period, a
          separate HECA measurement must be made for each task.
        </li>
        <li>
          When two or more crews are working in proximity to one another and
          performing the same task, they must be grouped as one HECA
          measurement.
        </li>
        <li>
          If two or more hazards have the same high-energy source and the same
          direct control, they must be combined as one entry.
        </li>
        <li>
          If there is a deficiency or missing coverage of a direct control,
          <sup>4</sup> the entry must be recorded as Exposure.
        </li>
        <li>
          Assessments must only be made based on work as it is observed.
          Hypothetical, anticipated, or speculated conditions should not be
          considered in the scoring.
        </li>
        <li>
          One object may involve more than one high-energy hazard.<sup>5</sup>
        </li>
        <li>
          Observers must make reasonable efforts to verify that direct controls
          are installed and used properly.
        </li>
        <li>
          The definitions of high energy and direct control must be strictly
          applied. The definitions are maintained by EEI’s
        </li>
        <li>Community of Practice(COP).</li>
      </ol>
      <hr className="mt-4 mb-4 border-t-2 border-gray-300" />
      <ol className=" list-outside text-justify space-y-2 text-sm">
        <li>
          <sup>2</sup>Incidents involve the release of energy. Incidents should
          be assessed and classified using the SCL model.
        </li>
        <li>
          <sup>3</sup>If tasks duration exceeds one working day, a separate HECA
          assessment should be made for each working day observed.
        </li>
        <li>
          <sup>4</sup>A direct control requires full coverage. Examples of
          deficiencies include incomplete coverage of flame-resistant (FR)
          clothing, part of the worker’s body (face, chest, etc.) exposed to an
          electrical hazard, or partial coverage of power lines with cover-up.
        </li>
        <li>
          <sup>5</sup>For example, a suspended load often involves gravity
          (falling load) and motion (swinging load).
        </li>
      </ol>
      <br />
      <Link
        href="https://www.eei.org/issues-and-policy/power-to-prevent-sif"
        target="_blank"
      >
        Source: https://www.eei.org/issues-and-policy/power-to-prevent-sif
      </Link>
    </div>
  );
};

export { HecaRulesForExelon, HecaRulesForXcelEnergy };
