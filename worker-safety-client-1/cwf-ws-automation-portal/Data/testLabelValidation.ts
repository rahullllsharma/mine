export const expectedEnergyComponents = [
    "CHEMICAL",
    "TEMPERATURE",
    "GRAVITY",
    "MOTION",
    "MECHANICAL",
    "ELECTRICAL",
    "PRESSURE",
    "SOUND",
    "RADIATION",
    "BIOLOGICAL",
  ] as const;

export const energyComponentColors = {
  BIOLOGICAL: "#6EC2D8",
  CHEMICAL: "#B7D771",
  TEMPERATURE: "#F38787",
  GRAVITY: "#3FD1AD",
  MOTION: "#ECDE65",
  MECHANICAL: "#E477A4",
  ELECTRICAL: "#EAB94C",
  PRESSURE: "#7FA6D9",
  SOUND: "#86D360",
  RADIATION: "#E89746",
} as const;
  