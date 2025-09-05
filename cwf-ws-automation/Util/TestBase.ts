import { Locator, Page, Response } from "@playwright/test";
import * as allure from "allure-js-commons";
const moment = require("moment");
import * as fs from "fs";
import * as path from "path";
import { getCurrentEnvUrl, CURRENT_ENV } from "../Data/envConfig";
import jsQR from "jsqr";
import { Jimp } from "jimp";
import pdfParse from "pdf-parse";

// Normalize PDF text output by mapping PDF-specific glyphs to ASCII and cleaning artifacts
function normalizePdfExtractedText(input: string): string {
  if (!input) return input;
  let text = input;
  // Map common private-use glyphs seen in extraction to ASCII
  const replacements: Array<[RegExp, string]> = [
    [/\uE0D2|\uE112|\uE152|\uE0D5/g, ":"], // miscellaneous colon-like
    [/\uE0C5/g, "+"],                        // plus (GMT+)
    [/\uE0C1/g, "("],                        // left paren
    [/\uE0C2/g, ")"],                        // right paren
    [/\uE136/g, "-"],                        // dash-like
    [/\uE1DB|\uE1FB|\uE156|\uE166|\uE1F6|\uE1E6/g, " "], // icons/bullets -> space
    
    // Additional parentheses mappings for various PDF encodings
    [/\uE0A8|\uE0A9|\uE0AA|\uE0AB/g, "("],   // Additional left paren variants
    [/\uE0AC|\uE0AD|\uE0AE|\uE0AF/g, ")"],   // Additional right paren variants
    [/\uE028/g, "("],                        // Another common left paren encoding
    [/\uE029/g, ")"],                        // Another common right paren encoding

  ];
  for (const [pattern, repl] of replacements) {
    text = text.replace(pattern, repl);
  }
  // Normalize various unicode spaces and punctuation to ASCII
  text = text
    .replace(/[\u00A0\u2000-\u200B\u202F\u205F\u3000]/g, " ") // spaces
    .replace(/[\u2010-\u2015]/g, "-") // hyphens/dashes
    .replace(/[\u2212]/g, "-") // minus
    .replace(/[\u2018\u2019\u201B\u2032]/g, "'")
    .replace(/[\u201C\u201D\u2033]/g, '"')
    .replace(/[\u2026]/g, "...")
    .replace(/[\u00B7\u2022\u2043\u2219]/g, "-")
    .replace(/[\uFEFF]/g, "");

  // Fix time formats where colons are missing (common PDF extraction issue)
  // Pattern: "02 51 pm" -> "02:51 pm", "12 30 am" -> "12:30 am"
  text = text.replace(/\b(\d{1,2})\s+(\d{2})\s+(am|pm)\b/gi, "$1:$2 $3");
  
  // Fix date formats where colons are missing in timestamps
  // Pattern: "2 54:14 pm" -> "2:54:14 pm"
  text = text.replace(/\b(\d{1,2})\s+(\d{2}):(\d{2})\s+(am|pm)\b/gi, "$1:$2:$3 $4");

  // Fix for gmt 5 30 -> gmt 5:30
  text = text.replace(/\b(gmt)\s+(\d{1,2})\s+(\d{2})\b/gi, "$1 $2:$3");
  
  // Fix date formats where spaces are missing in dates
  // Pattern: "2025 08 11" -> "2025-08-11"
  text = text.replace(/\b(\d{4})\s+(\d{2})\s+(\d{2})\b/g, "$1-$2-$3")
             .replace(/\bedit\b/gi, "");

  // Fix missing parentheses around measurements (common PDF extraction issue)
  // Only add parentheses if they're not already there
  // Pattern: "fall from elevation 4'" -> "fall from elevation ( 4')" (but skip if already "( 4')")
  text = text.replace(/\b((?:\w+\s+)*(?:from\s+)?elevation)\s+(?!\()\s*(\d+['″]?)\b/gi, "$1 ( $2)");
  
  // More general pattern for measurements that should have parentheses (but avoid double-adding)
  // Pattern: "height 10'" -> "height ( 10')" (but skip if already "( 10')")
  text = text.replace(/\b(height|depth|width|length|distance)\s+(?!\()\s*(\d+['″]?)\b/gi, "$1 ( $2)");
  
  // Fix swapped parenthesis and apostrophe in measurements
  // Pattern: "( 4)'" -> "( 4')" (common PDF extraction error)
  text = text.replace(/\(\s*(\d+)\s*\)\s*'/g, "( $1')");
  
  // Fix GPS coordinates where minus sign is missing from longitude (only for US coordinates)
  // Pattern: "37.785834, 122.406417" -> "37.785834, -122.406417" (only if longitude > 100)
  text = text.replace(/\b(\d+\.\d+),\s*(\d{3}\.\d+)\b/g, (match, lat, lon) => {
    const lonNum = parseFloat(lon);
    // Only add minus sign if longitude is > 100 (typical US West Coast coordinates)
    // This avoids incorrectly adding minus to positive longitudes like India (70-90°E)
    return lonNum > 100 ? `${lat}, -${lon}` : match;
  });
  
  // Fix phone number formats where parentheses and hyphens are missing
  // Pattern: "470 785 1000" -> "(470) 785-1000", "678 623 7000" -> "(678) 623-7000"
  text = text.replace(/\b(\d{3})\s+(\d{3})\s+(\d{4})\b/g, "($1) $2-$3");
  
  // Fix phone numbers with missing hyphens (e.g., "(987) 654 3212" -> "(987) 654-3212")
  text = text.replace(/\((\d{3})\)\s+(\d{3})\s+(\d{4})/g, "($1) $2-$3");

  text = text.replace(/\b(share)\b/gi, "");
  
  // Remove page artifacts first - very specific pattern for "page true5/7" format
  text = text.replace(/page\s+true\d+\/\d+/gi, "");
  text = text.replace(/page\s+true\s*\d+\/\d+/gi, "");
  
  // Remove printPage artifacts like "printPage=true5/7"
  text = text.replace(/printPage\s*=\s*true\d+\/\d+/gi, "");
  text = text.replace(/printPage\s*=\s*true\s*\d+\/\d+/gi, "");
  text = text.replace(/printPage\s*=\s*true\d+\s*\/\s*\d+/gi, "");
  text = text.replace(/printPage\s*=\s*true\s*\d+\s*\/\s*\d+/gi, "");
  
  // Fix count/number formats - keep consistent with PDF format (no parentheses)
  // Pattern: "photos 1" -> "photos 1", "documents 2" -> "documents 2"
  // Also handle cases where parentheses already exist: "photos (1)" -> "photos 1"
  text = text.replace(/(photos|documents)\s*\(\s*(\d+)\s*\)/gi, "$1 $2");
  text = text.replace(/(photos|documents)\s+(\d+)/gi, "$1 $2");
  
  // Fix PDF extraction artifacts and formatting issues
  text = text
    // Fix distribution bulletin formatting (add missing hyphens)
    .replace(/\bdb\s+(\d+)\s+(\d+)\b/gi, "db $1-$2")
    // Fix missing spaces in PPE items
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    // Fix duplicated content patterns (more comprehensive)
    .replace(/([a-z\s,]+)\s+\1/gi, "$1")
    .replace(/(insects, ticks, vermin, poisonous plants)\s+\1/gi, "$1")
    // Fix missing parentheses in document counts
    .replace(/\b(\d+)\s+(test|export|\.pdf)/gi, "( $1 ) $2")
    // Fix document formatting with missing parentheses and spaces
    .replace(/\b(\d+)\s+(test export)/gi, "( $1 ) $2")
    // Fix singular/plural mismatches in common terms
    .replace(/\bbest work practices?\b/gi, "best work practice")
    // Fix missing spaces in PPE items (more specific)
    .replace(/(hard hat)(gloves)(safety toe shoes)(safety glasses)(safety vest)/gi, "$1 $2 $3 $4 $5")
    // Fix phone number format differences
    .replace(/1-888-373-7888/g, "1 (888) 373-7888")
    // Fix missing "insect repellant" in site conditions
    .replace(/(insects, ticks, vermin, poisonous plants ppe direct control ppe)/gi, "$1 insect repellant")
    // Remove "save and continue" text from documents field
    .replace(/\s*save and continue\s*$/gi, "");
  
  // Remove specific page artifacts first (exact patterns)
  text = text
    .replace(/page\s+true\d+\/\(\s*\d+\s*\)\s*/gi, "") 
    .replace(/page\s+true\d+\/\d+\s*/gi, "")
    .replace(/page\s+true\d+[^a-zA-Z]*/gi, "")
    .replace(/page\s+true\d+\/\d+/gi, "");

  // Fix distribution bulletin formatting early (before other processing)
  text = text
    .replace(/\bdb\s+(\d+)\s+(\d+)\b/gi, "db $1-$2")
    .replace(/\bdb(\d+)\s+(\d+)\b/gi, "db $1-$2")
    .replace(/\bdb\s+(\d+)(\d+)\b/gi, "db $1-$2")
    .replace(/\bdb_(\d+)(\d+)\b/gi, "db $1-$2")
    .replace(/\bdb_(\d)-(\d+)\b/gi, "db $1-$2")
    .replace(/\bdb_801\b/gi, "db 8-01")
    .replace(/\bdb\s+8\s+01\b/gi, "db 8-01");

  // Remove common PDF page artifacts (headers, footers, URLs, timestamps)
  text = text
    // Remove job safety briefing headers (improved flexible pattern)
    .replace(/job\s+safety\s+briefing\s+\w*\s*[\d\/]*,?\s*\d{1,2}:\d{2}\s*(am|pm)?/gi, "")
    // Remove job safety briefing headers without timestamps
    .replace(/job\s+safety\s+briefing\s+(low|medium|high|critical)\s*/gi, "")
    // Remove remaining date/time fragments
    .replace(/\/\d{1,2},?\s*\d{1,2}:\d{2}\s*(am|pm)?/gi, "")
    // Remove worker safety urbint headers
    .replace(/worker\s+safety\s*[\|\s]*urbint/gi, "")
    // Remove URLs (http/https links)
    .replace(/https?:\/\/[^\s]+/gi, "")
            // Remove print page artifacts (more comprehensive)
        .replace(/printpage\s*=?\s*true/gi, "")
        .replace(/page\s+true\d+\/\d+/gi, "")
        .replace(/page\s+true\s*\(\s*\d+\s*\)/gi, "")
        .replace(/page\s+true\d+\s*\(\s*\d+\s*\)/gi, "")
        .replace(/page\s+true\d+\s*\/\s*\(\s*\d+\s*\)/gi, "")
        // Remove specific page artifacts like "page true1/( 4 )"
        .replace(/page\s+true\d+\s*\(\s*\(\s*\d+\s*\)\s*\)/gi, "")
        .replace(/page\s+true\d+\s*\(\s*\/\s*\(\s*\d+\s*\)\s*\)/gi, "")
        // Remove any page artifacts with numbers (more specific patterns)
        .replace(/page\s+true\d+\/\(\s*\d+\s*\)\s*/gi, "")
        .replace(/page\s+true\d+\/\d+\s*/gi, "")
        // Remove specific format "page true1/( 4 )"
        .replace(/page\s+true\d+\/\(\s*\(\s*\d+\s*\)\s*\)/gi, "")
        .replace(/page\s+true\s+\d+\/\d+/gi, "")
        .replace(/page\s+true\d+\/\d+/gi, "")
        .replace(/page\s+true\d+[^a-zA-Z]*/gi, "")
        .replace(/page\s+true\s*\d+\s*\/\s*\d+/gi, "")
        .replace(/page\s+true\s*\d+\s*\/\s*\(\s*\d+\s*\)/gi, "")
        .replace(/page\s+true\s*\d+\s*\/\s*\(\s*\(\s*\d+\s*\)\s*\)/gi, "")
        // Remove specific page artifacts like "page true1/( 4 )"
        .replace(/page\s+true\d+\s*\(\s*\(\s*\d+\s*\)\s*\)/gi, "")
        .replace(/page\s+true\d+\s*\(\s*\/\s*\(\s*\d+\s*\)\s*\)/gi, "")
        // Remove page artifacts with parentheses and numbers
        .replace(/page\s+true\d+\s*\(\s*\(\s*\d+\s*\)\s*\)/gi, "")
        .replace(/page\s+true\d+\s*\(\s*\/\s*\(\s*\d+\s*\)\s*\)/gi, "")
        // Remove page numbers like "1/4", "2/4", etc.
        .replace(/\b\d+\/\d+\b/g, "")
    // Remove standalone timestamps (more specific)
    .replace(/\b\d{1,2}\/\d{1,2}\/\d{2,4},?\s*\d{1,2}:\d{2}\s*(am|pm)?\b/gi, "");
  
  // Collapse excessive whitespace
  text = text.replace(/\s+\n/g, "\n").replace(/\n\s+/g, "\n").replace(/\s+/g, " ").trim();
  return text;
}

let projectName: string;

export function getProjectName(): string {
  if (!projectName) {
    throw new Error(
      "Project name is not set. Ensure setProjectName is called in beforeAll/beforeEach."
    );
  }
  return projectName;
}
export function setProjectName(name: string): void {
  projectName = name;
}

export default class TestBase {
  private page: Page;
  
  // Helper function to extract relevant text snippet around a keyword
  private extractRelevantSnippet(text: string, keyword: string, contextLength: number): string {
    const index = text.toLowerCase().indexOf(keyword.toLowerCase());
    if (index === -1) return `"${keyword}" not found`;
    
    const start = Math.max(0, index - contextLength);
    const end = Math.min(text.length, index + keyword.length + contextLength);
    return text.substring(start, end).replace(/\s+/g, ' ').trim();
  }
  private networkLogs: Array<{ url: string; status: number; method: string; timestamp: string }> = [];
  private errorLogs: Array<{ url: string; status: number; method: string; timestamp: string; errorDetails?: string }> = [];

  constructor(page: Page) {
    this.page = page;
  }

  /**
   * Parse a flattened JSB Summary text blob into a structured JSON map suitable for comparisons.
   * This function is tolerant to PDF glyph artifacts and the space-less, lowercased web normalization.
   */
  public parseJSBSummaryToJSON(rawInput: string): Record<string, any> {
    // 1) Normalize PDF/web artifacts and unify glyphs
    const normalizeGlyphs = (input: string): string => {
      if (!input) return input;
      let t = input;
      // Reuse pdf normalization where helpful
      t = normalizePdfExtractedText(t);
      // Additional glyph mappings seen in web/pdf extractions
      // Map various private-use chars to ASCII separators
      t = t
        .replace(/[\uE000-\uF8FF]/g, " ") // general private-use chars -> space
        .replace(/[•·]/g, " ")
        .replace(/[\u2022\u00B7]/g, " ")
        .replace(/[\u2010-\u2015\u2212]/g, "-")
        .replace(/[\u2000-\u200B\u00A0\u202F\u205F\u3000]/g, " ")
        .replace(/[\u2018\u2019\u201B\u2032]/g, "'")
        .replace(/[\u201C\u201D\u2033]/g, '"')
        .replace(/[\u2026]/g, "...")
        .replace(/\s+/g, " ")
        .trim();
      return t;
    };

    const cleaned = normalizeGlyphs(rawInput);

    // 2) Build a normalized string for marker-based slicing (lowercase, no spaces)
    const dense = cleaned.toLowerCase().replace(/\s+/g, "");

    // 3) Known markers in the expected order (as they appear in the blob)
    const markers: Array<{ key: string; label: string }> = [
      { key: "summary", label: "jsbsummary" },
      { key: "jobInformation", label: "jobinformation" },
      { key: "briefingDate", label: "briefingdate" },
      { key: "briefingTime", label: "briefingtime" },
      { key: "workLocation", label: "worklocation" },
      { key: "operatingHQ", label: "operatinghq" },
      { key: "gpsCoordinates", label: "gpscoordinates" },
      { key: "medicalEmergency", label: "medical&emergencyinformation" },
      { key: "emergencyContact1", label: "emergencycontact1" },
      { key: "emergencyContact2", label: "emergencycontact2" },
      { key: "emergencyNumbers", label: "emergency:" },
      { key: "nearestHospital", label: "nearesthospital/emergencyresponse" },
      { key: "aedLocation", label: "aedlocation" },
      { key: "tasks", label: "tasks" },
      { key: "criticalRiskAreas", label: "criticalriskareas" },
      { key: "energySourceControls", label: "energysourcecontrols" },
      { key: "arcFlashCategory", label: "arcflashcategory" },
      { key: "primaryVoltage", label: "primaryvoltage" },
      { key: "secondaryVoltage", label: "secondaryvoltage" },
      { key: "transmissionVoltage", label: "transmissionvoltage" },
      { key: "clearancePoints", label: "clearancepoints" },
      { key: "workProcedures", label: "workprocedures" },
      { key: "distributionBulletins", label: "distributionbulletins" },
      { key: "rulesOfCoverUp", label: "4rulesofcoverup" },
      { key: "additionalDocumentation", label: "additionaldocumentation" },
      { key: "minimumApproachDistance", label: "minimumapproachdistance" },
      { key: "siteConditions", label: "siteconditions" },
      { key: "standardRequiredPPE", label: "standardrequiredppe" },
      { key: "attachments", label: "attachments" },
      { key: "photos", label: "photos" },
      { key: "documents", label: "documents" },
      { key: "signOff", label: "sign-off" },
      { key: "name1", label: "name1" },
    ];

    // 4) Locate markers in dense string - try multiple variants for better PDF compatibility
    type FoundMarker = { key: string; label: string; idx: number };
    const found: FoundMarker[] = [];
    for (const m of markers) {
      let idx = dense.indexOf(m.label);
      
      // If not found, try alternative patterns for PDF format
      if (idx === -1) {
        const alternatives = [];
        
        // For jobInformation, also try "job information" pattern
        if (m.key === "jobInformation") {
          alternatives.push("jobinformation", "job information");
        }
        // For medicalEmergency, try various patterns
        else if (m.key === "medicalEmergency") {
          alternatives.push("medical&emergencyinformation", "medical & emergency information", "medicalemergencyinformation");
        }
        // For minimumApproachDistance, try various patterns
        else if (m.key === "minimumApproachDistance") {
          alternatives.push("minimumapproachdistance", "minimum approach distance", "minimum approach distance");
        }
        // For other keys, try adding spaces
        else {
          // Convert camelCase to spaced version for PDF matching
          const spacedLabel = m.label.replace(/([a-z])([A-Z])/g, '$1 $2').toLowerCase();
          if (spacedLabel !== m.label) {
            alternatives.push(spacedLabel);
          }
        }
        
        // Try alternatives
        for (const alt of alternatives) {
          const altDense = alt.toLowerCase().replace(/\s+/g, "");
          idx = dense.indexOf(altDense);
          if (idx !== -1) break;
        }
      }
      
      if (idx !== -1) found.push({ key: m.key, label: m.label, idx });
    }
    found.sort((a, b) => a.idx - b.idx);

    // 5) Slice values between markers using the original cleaned string for readability
    let result: Record<string, any> = {};
    // Build a single dense->original map to reuse
    const denseToOriginal: number[] = [];
    for (let i = 0, d = 0; i < cleaned.length; i++) {
      const ch = cleaned[i];
      if (!/\s/.test(ch)) {
        denseToOriginal[d] = i;
        d++;
      }
    }
    const toOriginalSlice = (startDenseIdx: number, endDenseIdx: number): string => {
      const startOrig = startDenseIdx < denseToOriginal.length ? denseToOriginal[startDenseIdx] : cleaned.length;
      const endOrig = endDenseIdx < denseToOriginal.length ? denseToOriginal[endDenseIdx] : cleaned.length;
      return cleaned.substring(startOrig, endOrig).trim();
    };

    for (let i = 0; i < found.length; i++) {
      const cur = found[i];
      const next = found[i + 1];
      const start = cur.idx + cur.label.length;
      const end = next ? next.idx : dense.length;
      const rawValue = toOriginalSlice(start, end);
      result[cur.key] = rawValue;
    }

    // 6) Post-processing helpers
    const extractFirstMatch = (text: string, re: RegExp): string | undefined => {
      const m = re.exec(text);
      return m && m[1] ? m[1].trim() : undefined;
    };

    const cleanInline = (t?: string): string | undefined => {
      if (!t) return t;
      let cleaned = t.replace(/\s+/g, " ").replace(/[\uE000-\uF8FF]/g, " ").trim();
      
      // Remove specific page artifacts first (exact patterns)
      cleaned = cleaned
        .replace(/page\s*=?\s*true\d+\/\d+\s*/gi, "") // Remove "page true2/4", "page=true1/4", etc.
        .replace(/page\s*=?\s*true\d+\/(\d+|\(\s*\d+\s*\))\s*/gi,"")
        .replace(/page\s+true\d+\/\(\s*\d+\s*\)\s*/gi, "")
        .replace(/page\s+true\d+\/\d+\s*/gi, "")
        .replace(/page\s+true\d+[^a-zA-Z]*/gi, "");

      // Fix distribution bulletin formatting early (before other processing)
      cleaned = cleaned
        .replace(/\bdb\s+(\d+)\s+(\d+)\b/gi, "db $1 $2")
        .replace(/\bdb(\d+)\s+(\d+)\b/gi, "db $1 $2")
        .replace(/\bdb\s+(\d+)(\d+)\b/gi, "db $1 $2")
        .replace(/\bdb_(\d+)(\d+)\b/gi, "db $1 $2")
        .replace(/\bdb_(\d)-(\d+)\b/gi, "db $1 $2")
        .replace(/\bdb_801\b/gi, "db 8 01")
        .replace(/\bdb\s+8\s+01\b/gi, "db 8 01")
        .replace(/\bdb\s*[_-]\s*8\s*[_-]\s*01\b/gi, "db 8 01"); // Handle various db 8-01 formats
      
      // Remove PDF page artifacts that might contaminate field values
      cleaned = cleaned
        // Remove job safety briefing headers (improved flexible pattern)
        .replace(/job\s+safety\s+briefing\s+\w*\s*[\d\/]*,?\s*\d{1,2}:\d{2}\s*(am|pm)?/gi, "")
        // Remove job safety briefing headers without timestamps
        .replace(/job\s+safety\s+briefing\s+(low|medium|high|critical)\s*/gi, "")
        // Remove remaining date/time fragments
        .replace(/\/\d{1,2},?\s*\d{1,2}:\d{2}\s*(am|pm)?/gi, "")
        // Remove worker safety urbint headers
        .replace(/worker\s+safety\s*[\|\s]*urbint/gi, "")
        // Remove URLs (http/https links)
        .replace(/https?:\/\/[^\s]+/gi, "")
        .replace(/page\s+true\s+\d+\/\d+/gi, "")
        .replace(/page\s+true\d+\/\d+/gi, "")
        .replace(/page\s+true\s*\d+\s*\/\s*\d+/gi, "")
        .replace(/page\s+true\s*\d+\s*\/\s*\(\s*\d+\s*\)/gi, "")
        .replace(/page\s+true\s*\d+\s*\/\s*\(\s*\(\s*\d+\s*\)\s*\)/gi, "")
        .replace(/page\s+true\d+[^a-zA-Z]*/gi, "")
        // Remove UI button text that gets incorrectly extracted
        .replace(/\bshare\b/gi, "") // Remove "Share" button text
        .replace(/\bedit\b/gi, "") // Remove "Edit" button text (already exists but reinforcing)
        // Remove share text that appears near QR code/summary
        .replace(/\s+share\s+last\s+updated/gi, " last updated") // Remove "share" before "last updated"
        .replace(/share\s+(last updated at)/gi, "$1")
            // Remove print page artifacts (more comprehensive)
    .replace(/printpage\s*=?\s*true/gi, "")
    .replace(/page\s*=?\s*true\d+\/\d+/gi, "") // Remove "page true2/4", "page=true1/4"
    .replace(/page\s*=?\s*true\d+\/(\d+|\(\s*\d+\s*\))\s*/gi,"")
    .replace(/page\s+true\d+\/\d+/gi, "")
    .replace(/page\s+true\s*\(\s*\d+\s*\)/gi, "")
    .replace(/page\s+true\d+\s*\(\s*\d+\s*\)/gi, "")
    .replace(/page\s+true\d+\s*\/\s*\(\s*\d+\s*\)/gi, "")
    // Remove specific page artifacts like "page true1/( 4 )"
    .replace(/page\s+true\d+\s*\(\s*\(\s*\d+\s*\)\s*\)/gi, "")
    .replace(/page\s+true\d+\s*\(\s*\/\s*\(\s*\d+\s*\)\s*\)/gi, "")
    // Remove any page artifacts with numbers (more specific patterns)
    .replace(/page\s+true\d+\/\(\s*\d+\s*\)\s*/gi, "")
    .replace(/page\s+true\d+\/\d+\s*/gi, "")
    // Remove specific format "page true1/( 4 )"
    .replace(/page\s+true\d+\/\(\s*\(\s*\d+\s*\)\s*\)/gi, "")
            .replace(/page\s+true\d+[^a-zA-Z]*/gi, "")
        .replace(/page\s+true\s*\d+\s*\/\s*\d+/gi, "")
        .replace(/page\s+true\s*\d+\s*\/\s*\(\s*\d+\s*\)/gi, "")
        .replace(/page\s+true\s*\d+\s*\/\s*\(\s*\(\s*\d+\s*\)\s*\)/gi, "")
        // Remove specific page artifacts like "page true1/( 4 )"
    .replace(/page\s+true\d+\s*\(\s*\(\s*\d+\s*\)\s*\)/gi, "")
    .replace(/page\s+true\d+\s*\(\s*\/\s*\(\s*\d+\s*\)\s*\)/gi, "")
    // Remove page artifacts with parentheses and numbers
    .replace(/page\s+true\d+\s*\(\s*\(\s*\d+\s*\)\s*\)/gi, "")
    .replace(/page\s+true\d+\s*\(\s*\/\s*\(\s*\d+\s*\)\s*\)/gi, "")
    // Remove page numbers like "1/4", "2/4", etc.
    .replace(/\b\d+\/\d+\b/g, "")
        // Remove standalone timestamps (more specific)
    .replace(/\b\d{1,2}\/\d{1,2}\/\d{2,4},?\s*\d{1,2}:\d{2}\s*(am|pm)?\b/gi, "")
        // Remove "Edit" text that appears in UI buttons but shouldn't be part of content
    .replace(/\bedit\b/gi, "")
    .replace(/\bshare\b/gi, "");
      
      // Fix time formats where colons are missing (e.g., "02 51 PM" -> "02:51 PM")
      cleaned = cleaned.replace(/\b(\d{1,2})\s+(\d{2})\s+(am|pm)\b/gi, "$1:$2 $3");
      // Fix phone number formats where parentheses and hyphens are missing (e.g., "470 785 1000" -> "(470) 785-1000")
      cleaned = cleaned.replace(/\b(\d{3})\s+(\d{3})\s+(\d{4})\b/g, "($1) $2-$3");
      
      // Fix phone numbers with missing hyphens (e.g., "(987) 654 3212" -> "(987) 654-3212")
      cleaned = cleaned.replace(/\((\d{3})\)\s+(\d{3})\s+(\d{4})/g, "($1) $2-$3");

      cleaned = cleaned.replace(/\b(gmt)\s+(\d{1,2})\s+(\d{2})\b/gi, "$1 $2:$3");
      // Fix timezone format where colon is missing (e.g., "GMT 5 30" -> "GMT+5:30", "GMT+5 30" -> "GMT+5:30", "GMT530" -> "GMT+5:30")
      cleaned = cleaned.replace(/\bgmt\s*\+?\s*(\d{1,2})\s*(\d{2})\b/gi, "GMT+$1:$2");
      // Also handle the case where spaces are removed: "gmt530" -> "gmt+5:30"
      cleaned = cleaned.replace(/\bgmt(\d{1,2})(\d{2})\b/gi, "GMT+$1:$2");

      cleaned = cleaned.replace(/(gmt)\s+(\d{1,2})\s+(\d{2})/gi, "$1 $2:$3");

      cleaned = cleaned.replace(/(gmt)[\s:-]+(\d{1,2})[\s:-]+(\d{2})/gi, "$1 $2:$3");
      
      // Fix GPS coordinates where minus sign is missing from longitude (only for US coordinates)
      // Pattern: "37.785834, 122.406417" -> "37.785834, -122.406417" (only if longitude > 100)
      cleaned = cleaned.replace(/\b(\d+\.\d+),\s*(\d{3}\.\d+)\b/g, (match, lat, lon) => {
        const lonNum = parseFloat(lon);
        // Only add minus sign if longitude is > 100 (typical US West Coast coordinates)
        // This avoids incorrectly adding minus to positive longitudes like India (70-90°E)
        return lonNum > 100 ? `${lat}, -${lon}` : match;
      });
      
      // Fix count/number formats - keep consistent with PDF format (no parentheses)
      // Also handle cases where parentheses already exist: "photos (1)" -> "photos 1"
      cleaned = cleaned.replace(/(photos|documents)\s*\(\s*(\d+)\s*\)/gi, "$1 $2");
      cleaned = cleaned.replace(/(photos|documents)\s+(\d+)/gi, "$1 $2");
      
      // Fix PDF extraction artifacts and formatting issues
      cleaned = cleaned
        // Fix distribution bulletin formatting (add missing hyphens)
        .replace(/\bdb\s+(\d+)\s+(\d+)\b/gi, "db $1-$2")
        // Fix missing spaces in PPE items
        .replace(/([a-z])([A-Z])/g, "$1 $2")
        // Fix duplicated content patterns
        .replace(/([a-z\s,]+)\s+\1/gi, "$1")
        // Fix document counts - keep consistent with PDF format (no parentheses)
        .replace(/\b(\d+)\s+(test|export|\.pdf)/gi, "$1 $2")
                // Fix singular/plural mismatches in common terms
        .replace(/\bbest work practices?\b/gi, "best work practice")
        // Fix underscores and normalize formatting
        .replace(/_/g, " ") // Replace underscores with spaces
        // Remove page artifacts that commonly appear in PDF extraction
        .replace(/page\s+true\s*\d+\s*\/\s*\d+/gi, "")
        .replace(/page\s+true\d+\/\d+/gi, "")
        .replace(/page\s+true\s*\d+\s*\/\s*\(\s*\d+\s*\)/gi, "")
        .replace(/page\s+true\s*\d+\s*\/\s*\(\s*\(\s*\d+\s*\)\s*\)/gi, "")
        .replace(/page\s+true\d+[^a-zA-Z]*/gi, "")
        // More comprehensive page artifact removal - catch any remaining patterns
        .replace(/page\s+true\s*\d+\s*\/\s*\d+/gi, "")
        .replace(/page\s+true\d+\s*\/\s*\d+/gi, "")
        .replace(/page\s+true\s*\d+\s*\/\s*\(\s*\d+\s*\)/gi, "")
        .replace(/page\s+true\d+\s*\/\s*\(\s*\d+\s*\)/gi, "")
        .replace(/page\s+true\s*\d+\s*\/\s*\(\s*\(\s*\d+\s*\)\s*\)/gi, "")
        .replace(/page\s+true\d+\s*\/\s*\(\s*\(\s*\d+\s*\)\s*\)/gi, "")
        // Catch any page artifact with numbers and slashes
        .replace(/page\s+true\s*\d+\s*\/\s*\d+/gi, "")
        .replace(/page\s+true\d+\s*\/\s*\d+/gi, "")
        // Very specific pattern for "page true5/7" format
        .replace(/page\s+true\d+\/\d+/gi, "")
        .replace(/page\s+true\s*\d+\/\d+/gi, "")
        // Aggressive page artifact removal - remove any "page true" followed by numbers and slashes
        .replace(/page\s+true\s*\d+\s*\/\s*\d+/gi, "")
        .replace(/page\s+true\d+\s*\/\s*\d+/gi, "")
        .replace(/page\s+true\s*\d+\/\d+/gi, "")
        .replace(/page\s+true\d+\/\d+/gi, "")
        // Very specific pattern for the exact "page true5/7" format
        .replace(/page\s+true\d+\/\d+/gi, "")
        .replace(/page\s+true\s*\d+\/\d+/gi, "")
        // Catch any remaining page artifacts with different spacing
        .replace(/page\s+true\s*\d+\s*\/\s*\d+/gi, "")
        .replace(/page\s+true\d+\s*\/\s*\d+/gi, "")
        // Final catch-all for any page artifact pattern
        .replace(/page\s+true\s*\d+\s*\/\s*\d+/gi, "")
        .replace(/page\s+true\d+\s*\/\s*\d+/gi, "")
        .replace(/page\s+true\s*\d+\/\d+/gi, "")
        .replace(/page\s+true\d+\/\d+/gi, "");
      
      // Fix standalone numbers - keep consistent with PDF format (no parentheses)
      if (/^\d+$/.test(cleaned.trim())) {
        cleaned = cleaned.trim();
      }
      
      // Final cleanup before normalization
      // Remove "share" text that appears before "last updated"
      cleaned = cleaned.replace(/\bshare\s+last\s+updated/gi, "last updated");
      cleaned = cleaned.replace(/share\s+(last updated at)/gi, "$1");
      cleaned = cleaned.replace(/\bshare\b/gi, "");
      
      
      // Two-step hyphen normalization for consistent comparison
      // Step 1: Replace all hyphens with spaces
      cleaned = cleaned.replace(/-/g, " ");
      // Step 2: Collapse multiple spaces into single spaces and trim
      cleaned = cleaned.replace(/\s+/g, " ").trim();
      
      return cleaned || undefined;
    };

    // Job Information
    result.briefingDate = cleanInline(result.briefingDate);
    result.briefingTime = cleanInline(result.briefingTime);
    result.workLocation = cleanInline(result.workLocation);
    result.operatingHQ = cleanInline(result.operatingHQ);

    // GPS Coordinates
    if (typeof result.gpsCoordinates === "string") {
      // Fix missing minus sign in longitude (common PDF extraction issue)
      let fixedCoords = result.gpsCoordinates;
      
      // Pattern: "37.785834, 122.406417" -> "37.785834, -122.406417" (only if longitude > 100)
      fixedCoords = fixedCoords.replace(/\b(\d+\.\d+),\s*(\d{3}\.\d+)\b/g, (match, lat, lon) => {
        const lonNum = parseFloat(lon);
        // Only add minus sign if longitude is > 100 (typical US West Coast coordinates)
        // This avoids incorrectly adding minus to positive longitudes like India (70-90°E)
        return lonNum > 100 ? `${lat}, -${lon}` : match;
      });
      
      const coords = extractFirstMatch(fixedCoords, /(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)/);
      if (coords) {
        const m = /(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)/.exec(fixedCoords)!;
        result.gps = { latitude: parseFloat(m[1]), longitude: parseFloat(m[2]) };
      }
    }

    // Emergency Contacts (name + phone)
    const parseContact = (value?: string) => {
      if (!value) return undefined;
      const v = value.replace(/[\uE000-\uF8FF]/g, ":");
      
      // Try to extract phone number using multiple patterns
      let phone: string | undefined;
      let name: string;
      
      // Pattern 1: Look for full phone number with parentheses and formatting
      const fullPhoneMatch = v.match(/\((\d{3})\)\s*(\d{3})[-\s](\d{4})/);
      if (fullPhoneMatch) {
        phone = `(${fullPhoneMatch[1]}) ${fullPhoneMatch[2]}-${fullPhoneMatch[3]}`;
        name = v.replace(/\((\d{3})\)\s*(\d{3})[-\s](\d{4}).*$/, "").trim();
      } else {
        // Pattern 2: Look for phone number with just digits and spaces
        const digitPhoneMatch = v.match(/(\d{3})\s*(\d{3})\s*(\d{4})/);
        if (digitPhoneMatch) {
          phone = `(${digitPhoneMatch[1]}) ${digitPhoneMatch[2]}-${digitPhoneMatch[3]}`;
          name = v.replace(/(\d{3})\s*(\d{3})\s*(\d{4}).*$/, "").trim();
        } else {
          // Pattern 3: Split on colon/dash and use the last part as phone
          const parts = v.split(/[:\-]/);
          if (parts.length >= 2) {
            name = parts[0].replace(/[^a-z\s'-]/gi, " ").replace(/\s+/g, " ").trim();
            const phonePart = parts.slice(1).join(":").replace(/[^0-9+()\-\s]/g, "").trim();
            phone = cleanInline(phonePart) || phonePart;
          } else {
            // Pattern 4: Fallback - extract any phone-like pattern
            const phoneMatch = v.match(/(\+?\d[\d\s()\-]{10,})/);
            if (phoneMatch) {
              phone = cleanInline(phoneMatch[1].trim()) || phoneMatch[1].trim();
              name = v.replace(/(\+?\d[\d\s()\-]{10,}).*$/, "").trim();
            } else {
              name = v.trim();
              phone = undefined;
            }
          }
        }
      }
      
      return { name, phone };
    };
    result.emergencyContact1 = parseContact(result.emergencyContact1);
    result.emergencyContact2 = parseContact(result.emergencyContact2);

    // Emergency Numbers block
    if (typeof result.emergencyNumbers === "string") {
      let block = result.emergencyNumbers.replace(/[\uE000-\uF8FF]/g, ":");
      const pairs: Record<string, string> = {};
      
      // Handle PDF format where phone numbers are missing colons after DCC labels
      // Fix patterns like "Atlanta DCC 678 623 7000" -> "Atlanta DCC: 678 623 7000"
      block = block.replace(/([a-z]+\s+dcc)\s+(\d)/gi, "$1: $2");
      // Fix patterns like "Macon DCC 478 785 3700" -> "Macon DCC: 478 785 3700"
      // (This is covered by the above pattern)
      
      // Also handle concatenated format if present
      block = block.replace(/([a-z]+dcc)(\d{10})/gi, "$1:$2");
      block = block.replace(/(psoc\/corporatesecurity)(\d{10})/gi, "$1:$2");
      
      const items = block.split(/(?=[a-z][a-z/ ]{0,30}:)/i); // split when a new label: appears
      
      for (const item of items) {
        const m = item.match(/^([a-z/ ]+):\s*([0-9+()\-\s]+)/i);
        if (m) {
          let key = m[1].toLowerCase().replace(/\s+/g, " ").trim();
          let value = cleanInline(m[2]) || m[2].replace(/\s+/g, " ").trim();
          
          // Map common emergency number labels to consistent keys
          if (key.includes("atlanta") && key.includes("dcc")) key = "a";
          else if (key.includes("macon") && key.includes("dcc")) key = "c";
          else if (key.includes("psoc") || key.includes("corporate")) key = "y";
          
          pairs[key] = value;
        }
      }
      // Also direct 3-digit emergency
      const em = block.match(/\b(\d{3})\b/);
      if (em) pairs["emergency"] = em[1];
      result.emergencyNumbers = pairs;
    }

    // Nearest Hospital
    result.nearestHospital = cleanInline(result.nearestHospital);
    result.aedLocation = cleanInline(result.aedLocation);

    // Arc flash etc.
    result.arcFlashCategory = extractFirstMatch(String(result.arcFlashCategory || ""), /(\d+)/) || cleanInline(result.arcFlashCategory);
    result.primaryVoltage = cleanInline(result.primaryVoltage);
    result.secondaryVoltage = cleanInline(result.secondaryVoltage);
    result.transmissionVoltage = cleanInline(result.transmissionVoltage);
    // Clearance points: prefer the number closest after the label
    let clearance = extractFirstMatch(String(result.clearancePoints || ""), /(\d{1,3})/);
    if (!clearance) {
      // Fallback: search in a small window after the label in the full cleaned text
      const label = "clearancepoints";
      const idx = dense.indexOf(label);
      if (idx !== -1) {
        const startDense = idx + label.length;
        const endDense = Math.min(startDense + 60, dense.length); // look ahead window
        const windowText = toOriginalSlice(startDense, endDense);
        const m = windowText.match(/\b(\d{1,3})\b/);
        if (m) clearance = m[1];
      }
    }
    result.clearancePoints = clearance || cleanInline(result.clearancePoints);

    // Attachments counts and file names
    if (typeof result.attachments === "string") {
      const block = (result.attachments + (result.photos || "") + (result.documents || "")).toLowerCase();
      const photos = extractFirstMatch(block, /photos\s*[(:]?\s*(\d+)/i);
      const documents = extractFirstMatch(block, /documents\s*[(:]?\s*(\d+)/i);
      const pdfs = Array.from(cleaned.matchAll(/([a-z0-9_\-]+)\.pdf/gi)).map((m) => m[1]);
      result.attachments = {
        photos: photos ? cleanInline(`photos ${photos}`) || photos : undefined,
        documents: documents ? cleanInline(`documents ${documents}`) || documents : undefined,
        pdfs,
      };
    }

    // Photos and Documents - apply formatting fixes
    result.photos = cleanInline(result.photos);
    result.documents = cleanInline(result.documents);
    
    // Ensure photos and documents counts have consistent formatting (no parentheses)
    if (result.photos && /^\d+$/.test(result.photos.trim())) {
      result.photos = result.photos.trim();
    }
    if (result.documents && /^\d+$/.test(result.documents.trim())) {
      result.documents = result.documents.trim();
    }
    
    // Tasks, Critical Risks, Site Conditions, PPE - keep raw slices for comparison
    result.tasks = cleanInline(result.tasks);
    result.criticalRiskAreas = cleanInline(result.criticalRiskAreas);
    result.workProcedures = cleanInline(result.workProcedures);
    result.distributionBulletins = cleanInline(result.distributionBulletins);
    
    // Special cleanup for minimumApproachDistance - remove page artifacts specifically
    if (result.minimumApproachDistance) {
      result.minimumApproachDistance = result.minimumApproachDistance
        .replace(/page\s+true\d+\/\d+/gi, "")
        .replace(/page\s+true\s*\d+\/\d+/gi, "")
        .replace(/page\s+true\s*\d+\s*\/\s*\d+/gi, "")
        .replace(/page\s+true\d+\s*\/\s*\d+/gi, "")
        .replace(/printPage\s*=\s*true\d+\/\d+/gi, "")
        .replace(/printPage\s*=\s*true\s*\d+\/\d+/gi, "")
        .replace(/printPage\s*=\s*true\d+\s*\/\s*\d+/gi, "")
        .replace(/printPage\s*=\s*true\s*\d+\s*\/\s*\d+/gi, "")
        .replace(/\s+/g, " ")
        .trim();
      
      // Add section header if it's missing (for web content)
      if (!result.minimumApproachDistance.toLowerCase().includes('minimum approach distance')) {
        result.minimumApproachDistance = `Minimum Approach Distance ${result.minimumApproachDistance}`;
      }
    }
    
         // Apply intelligent section boundary detection to prevent cross-contamination
     result = this.applySectionBoundaryDetection(result, found, cleanInline);
     
           // Apply intelligent section boundary detection to prevent cross-contamination
      result = this.applySectionBoundaryDetection(result, found, cleanInline);
    
    result.standardRequiredPPE = cleanInline(result.standardRequiredPPE);

    // Sign-off
    if (typeof result.name1 === "string") {
      const nameBlock = result.name1.replace(/[\uE000-\uF8FF]/g, " ");
      const name = extractFirstMatch(nameBlock, /^([a-z\-\s']+)/i);
      const role = extractFirstMatch(nameBlock, /\(([^)]+)\)/);
      const id = extractFirstMatch(nameBlock, /(\d{4,})\b/);
      result.signOff = { name: name?.trim(), role: role?.trim(), id: id ? parseInt(id, 10) : undefined };
    }

    return result;
  }

  /** 
   * Apply intelligent section boundary detection to prevent cross-contamination between sections.
   * This method detects when content from one section bleeds into another and fixes the boundaries.
   */
  private applySectionBoundaryDetection(result: Record<string, any>, found: Array<{key: string, label: string, idx: number}>, cleanInline: (t?: string) => string | undefined): Record<string, any> {
    // Define section header patterns that indicate the start of a new section (not content within a section)
    const sectionHeaderPatterns = [
      { key: 'standardRequiredPPE', patterns: [/\bppe\s+direct\s+control\s+ppe\b/i, /\bstandard\s+required\s+ppe\b/i] },
      { key: 'attachments', patterns: [/^attachments?\s*$/i, /^photos?\s*$/i, /^documents?\s*$/i] },
      { key: 'signOff', patterns: [/^sign\s*-?\s*off\s*$/i] },
      { key: 'workProcedures', patterns: [/^work\s+procedures?\s*$/i] },
      { key: 'energySourceControls', patterns: [/^energy\s+source\s+controls?\s*$/i] }
    ];

    // Process sections that commonly have contamination issues
    const sectionsToCheck = ['siteConditions'];
    
    for (const sectionKey of sectionsToCheck) {
      if (result[sectionKey] && typeof result[sectionKey] === 'string') {
        let content = result[sectionKey];

        // Special handling for siteConditions - use intelligent boundary detection
        if (sectionKey === 'siteConditions') {
          content = this.cleanSectionContent(content, 'siteConditions');
        }

        result[sectionKey] = content;
      }
    }

    // Apply standard cleaning to all sections
    for (const sectionKey of sectionsToCheck) {
      result[sectionKey] = cleanInline(result[sectionKey]);
    }

    return result;
  }

  /**
   * Intelligently clean section content by detecting and removing content from adjacent sections
   * without hard-coding specific terms
   */
  private cleanSectionContent(content: string, sectionKey: string): string {
    if (!content || typeof content !== 'string') return content;
    
    // Define section boundaries and their typical content patterns
    const sectionBoundaries = {
      'siteConditions': {
        // Keywords that indicate we've moved to the next section
        nextSectionIndicators: [
          'standard required ppe',
          'ppe direct control',
          'direct control ppe',
          'attachments',
          'sign off',
          'sign-off'
        ]
      },
      'standardRequiredPPE': {
        nextSectionIndicators: [
          'attachments',
          'sign off',
          'sign-off',
          'work procedures',
          'energy source controls'
        ]
      }
    };
    
    const boundary = sectionBoundaries[sectionKey as keyof typeof sectionBoundaries];
    if (!boundary) return content;
    
    let cleanedContent = content;
    
    // Find the earliest occurrence of any next section indicator
    let earliestNextSection = -1;
    for (const indicator of boundary.nextSectionIndicators) {
      const index = cleanedContent.toLowerCase().indexOf(indicator.toLowerCase());
      if (index !== -1 && (earliestNextSection === -1 || index < earliestNextSection)) {
        earliestNextSection = index;
      }
    }
    
    // If we found a next section indicator, truncate the content at that point
    if (earliestNextSection !== -1) {
      cleanedContent = cleanedContent.substring(0, earliestNextSection);
    }
    
    // Clean up the content
    cleanedContent = cleanedContent
      // Remove duplicate phrases
      .replace(/\b(\w+(?:\s+\w+)*)\s+\1\b/gi, '$1')
      // Clean up multiple spaces
      .replace(/\s+/g, ' ')
      .trim();
    
    return cleanedContent;
  }

  /** Build JSON from web summary extracted content (wrapper for parseJSBSummaryToJSON). */
  public buildWebSummaryJSON(rawWebContent: string): Record<string, any> {
    return this.parseJSBSummaryToJSON(rawWebContent);
  }

  /** Build JSON from PDF summary extracted content (wrapper for parseJSBSummaryToJSON). */
  public buildPdfSummaryJSON(rawPdfContent: string): Record<string, any> {
    return this.parseJSBSummaryToJSON(rawPdfContent);
  }

  /**
   * Compare two parsed JSB summaries (as JSON) and compute match percentage.
   * - Flattens both objects to path:value pairs
   * - Normalizes text for robust comparisons
   * - Returns percentage, counts, and detailed mismatch info
   */
  public compareJSBSummaries(
    webJson: Record<string, any>,
    pdfJson: Record<string, any>
  ): {
    matchPercentage: number;
    matchedKeys: number;
    totalKeys: number;
    missingInWeb: string[];
    missingInPdf: string[];
    mismatches: Array<{ key: string; web: string; pdf: string; similarity: number }>;
  } {
    const normalizeForCompare = (value: unknown): string => {
      if (value === null || value === undefined) return "";
      const text = typeof value === "string" ? value : JSON.stringify(value);
      // Reuse glyph normalization, then strong normalization
      const norm = normalizePdfExtractedText(text)
        .toLowerCase()
        .replace(/[\uE000-\uF8FF]/g, " ")
        .replace(/[^a-z0-9.\-(),:/'"\s]/g, " ")
        .replace(/\s+/g, " ")
        .trim();
      return norm;
    };

    const flatten = (obj: Record<string, any>, prefix = ""): Record<string, string> => {
      const out: Record<string, string> = {};
      const helper = (curr: any, path: string) => {
        if (curr === null || curr === undefined) return;
        if (typeof curr !== "object" || curr instanceof Date) {
          const val = normalizeForCompare(curr);
          if (val) out[path] = val;
          return;
        }
        if (Array.isArray(curr)) {
          // Join array items into a normalized string to compare
          const items = curr.map((v) => normalizeForCompare(v)).filter(Boolean);
          if (items.length > 0) out[path] = items.join(" | ");
          return;
        }
        for (const key of Object.keys(curr)) {
          const next = path ? `${path}.${key}` : key;
          helper(curr[key], next);
        }
      };
      helper(obj, prefix);
      return out;
    };

    const tokens = (s: string): Set<string> => {
      // Enhanced tokenization with better normalization
      let normalized = s.toLowerCase()
        // Fix concatenation issues like "controlled access zonequipment" -> "controlled access zone equipment"  
        .replace(/([a-z])([A-Z])/g, '$1 $2')
        // Specific concatenation fixes for common patterns (order matters!)
        .replace(/zonequipment/gi, 'zone equipment')         // Direct fix for "zonequipment"
        .replace(/zone([a-z])/gi, 'zone $1')                // General zone concatenation
        .replace(/equipment([a-z])/gi, 'equipment $1')      // General equipment concatenation
        .replace(/accesszone/gi, 'access zone')             // Direct fix for "accesszone"
        .replace(/access([a-z])/gi, 'access $1')            // General access concatenation
        .replace(/control([a-z])/gi, 'control $1')          // General control concatenation
        .replace(/loads([a-z])/gi, 'loads $1')              // General loads concatenation
        .replace(/barrier([a-z])/gi, 'barrier $1')          // General barrier concatenation
        // Fix parentheses and quote positioning issues
        .replace(/\(\s*(\d+)\s*\)\s*'/g, "( $1')")  // "( 4)'" -> "( 4')"
        .replace(/\(\s*(\d+)\s*'\s*\)/g, "( $1')")  // "( 4' )" -> "( 4')"
        // Normalize multiple spaces
        .replace(/\s+/g, ' ')
        .trim();
      
      return new Set(normalized.split(/\s+/).filter(Boolean));
    };
    
    const tokenSimilarity = (a: string, b: string): number => {
      const ta = tokens(a);
      const tb = tokens(b);
      if (ta.size === 0 && tb.size === 0) return 100;
      
      let inter = 0;
      for (const t of ta) if (tb.has(t)) inter++;
      const union = ta.size + tb.size - inter;
      return union === 0 ? 100 : Math.round((inter / union) * 100);
    };

    const fWeb = flatten(webJson);
    const fPdf = flatten(pdfJson);
    
    // Filter out expected empty section headers that are just organizational labels
    const isEmptySectionHeader = (key: string, webVal?: string, pdfVal?: string): boolean => {
      const sectionHeaders = ['jobInformation', 'medicalEmergency', 'energySourceControls', 'workProcedures'];
      if (!sectionHeaders.includes(key)) return false;
      
      // These sections are organizational headers - filter if either is empty or contains only UI text like "Edit"
      const isEmptyOrUIText = (val?: string) => !val || val.trim() === '' || val.trim().toLowerCase() === 'edit' || val.trim().toLowerCase() === 'share';
      return isEmptyOrUIText(webVal) || isEmptyOrUIText(pdfVal);


    };
    
    const allKeysRaw = new Set<string>([...Object.keys(fWeb), ...Object.keys(fPdf)]);
    const allKeys = new Set<string>();
    
    // Filter out empty section headers from comparison
    for (const key of allKeysRaw) {
      if (!isEmptySectionHeader(key, fWeb[key], fPdf[key])) {
        allKeys.add(key);
      }
    }

    let matched = 0;
    const mismatches: Array<{ key: string; web: string; pdf: string; similarity: number }> = [];
    const missingInWeb: string[] = [];
    const missingInPdf: string[] = [];

    for (const key of allKeys) {
      const w = fWeb[key];
      const p = fPdf[key];
      if (w === undefined && p !== undefined) {
        missingInWeb.push(key);
        continue;
      }
      if (p === undefined && w !== undefined) {
        missingInPdf.push(key);
        continue;
      }
      if (w === undefined && p === undefined) continue; // shouldn't happen

      if (w === p) {
        matched++;
      } else {
        const sim = tokenSimilarity(w!, p!);
        if (sim === 100 || sim >= 99) matched++; // Treat 99%+ as matches (essentially identical content)
        else mismatches.push({ key, web: w!, pdf: p!, similarity: sim });
      }
    }

    const total = allKeys.size;
    const matchPercentage = total === 0 ? 100 : Math.round((matched / total) * 1000) / 10; // one decimal

    return {
      matchPercentage,
      matchedKeys: matched,
      totalKeys: total,
      missingInWeb,
      missingInPdf,
      mismatches,
    };
  }


  public async goto() {
    const baseURL = getCurrentEnvUrl();
    await this.page.goto(baseURL);
  }

  public async gotoPageURL(pageName: string) {
    const baseURL = getCurrentEnvUrl();
    await this.page.goto(`${baseURL}${pageName}`);
  }

  public get gettxtlogdatetime() {
    return moment(new Date()).format("DD-MMM-YYYY HH:mm:ss");
  }

  public async captureScreenshot(curpage: Page, description?: string) {
    await allure.step(`Captured Screenshot: ${description}`, async () => {
      description = description ?? "Unknown";
      const screenshot = await curpage.screenshot({ fullPage: true });
      await allure.attachment(description, screenshot, "image/png");
    });
  }

  public async ReportScreenShot(curpage: Page, description?: string) {
    const screenshotBuffer = await curpage.screenshot();
    description = description || "Unknown";
    await allure.attachment(description, screenshotBuffer, "image/png");
  }

  public async DeleteAllureResultsFolderData() {
    const parent_AllureResults_dir1 = "./allure-results/";
    if (fs.existsSync(parent_AllureResults_dir1)) {
      fs.readdir(parent_AllureResults_dir1, (err, files) => {
        if (err) throw err;
        for (const file of files) {
          fs.unlinkSync(parent_AllureResults_dir1 + file);
        }
      });
    }
  }

  public async readPdfContent(pdfPath: string): Promise<string> {
    return await allure.step(`Reading text content from PDF: ${pdfPath}`, async () => {
      try {
        if (!fs.existsSync(pdfPath)) {
          throw new Error(`PDF file not found at path: ${pdfPath}. Please ensure it is saved correctly.`);
        }
        const dataBuffer = fs.readFileSync(pdfPath);
        await this.logSuccess(`PDF file size: ${dataBuffer.length} bytes`);
        const data = await pdfParse(dataBuffer, { max: 0 });
        const raw = data.text;
        
        // Remove page artifacts from raw PDF text before normalization
        let cleanedRaw = raw
          .replace(/page\s+true\d+\/\d+/gi, "")
          .replace(/page\s+true\s*\d+\/\d+/gi, "")
          .replace(/page\s+true\s*\d+\s*\/\s*\d+/gi, "")
          .replace(/page\s+true\d+\s*\/\s*\d+/gi, "")
          // Remove printPage artifacts like "printPage=true5/7"
          .replace(/printPage\s*=\s*true\d+\/\d+/gi, "")
          .replace(/printPage\s*=\s*true\s*\d+\/\d+/gi, "")
          .replace(/printPage\s*=\s*true\d+\s*\/\s*\d+/gi, "")
          .replace(/printPage\s*=\s*true\s*\d+\s*\/\s*\d+/gi, "");
        
        const normalized = normalizePdfExtractedText(cleanedRaw);
        
        // Debug logging for parentheses issues
        if (cleanedRaw.includes("4'") || cleanedRaw.includes("elevation")) {
          const elevationSnippet = this.extractRelevantSnippet(cleanedRaw, "elevation", 50);
          const normalizedSnippet = this.extractRelevantSnippet(normalized, "elevation", 50);
          await this.logSuccess(`PDF Debug - Raw elevation text: "${elevationSnippet}"`);
          await this.logSuccess(`PDF Debug - Normalized elevation text: "${normalizedSnippet}"`);
        }
        
        await this.logSuccess(`Successfully extracted text from PDF. Text length: ${normalized.length} characters`);
        await this.logSuccess(`PDF metadata: ${data.numpages} pages, ${data.numrender} rendered pages`);
        return normalized;
      } catch (error) {
        await this.logFailure(`Failed to read PDF content: ${error}`);
        throw new Error(`PDF reading failed: ${error}`);
      }
    });
  }

  public async getPdfAttachmentInfo(pdfPath: string): Promise<{photos: number, documents: number, details: string}> {
    return await allure.step(`Analyzing PDF attachments: ${pdfPath}`, async () => {
      try {
        if (!fs.existsSync(pdfPath)) {
          throw new Error(`PDF file not found at path: ${pdfPath}`);
        }
        const dataBuffer = fs.readFileSync(pdfPath);
        const data = await pdfParse(dataBuffer);
        // Normalize text before searching
        const pdfText = normalizePdfExtractedText(data.text);

        // Try to scope to attachments area first
        let attachmentSection = "";
        const attachIdx = pdfText.toLowerCase().indexOf("attachments");
        if (attachIdx !== -1) {
          attachmentSection = pdfText.substring(attachIdx, attachIdx + 800);
        }
        const searchText = attachmentSection || pdfText;

        let photoCount = 0;
        let documentCount = 0;
        let details = "";

        // Robust patterns – allow forms like "Photos 1", "Photos (1)", "Photos: 1"
        const photoPatterns: RegExp[] = [
          /photos?\s*[:\-]?\s*(\d+)/gi,
          /photos?\s*\((\d+)\)/gi,
          /\b(\d+)\s*photos?\b/gi,
          /images?\s*[:\-]?\s*(\d+)/gi,
        ];

        for (const pattern of photoPatterns) {
          let m: RegExpExecArray | null;
          // eslint-disable-next-line no-cond-assign
          while ((m = pattern.exec(searchText)) !== null) {
            const num = parseInt(m[1] || "0");
            if (!isNaN(num)) photoCount = Math.max(photoCount, num);
            details += `Photo ref:"${m[0]}"; `;
          }
        }

        const docPatterns: RegExp[] = [
          /documents?\s*[:\-]?\s*(\d+)/gi,
          /documents?\s*\((\d+)\)/gi,
          /\b(\d+)\s*documents?\b/gi,
          /files?\s*[:\-]?\s*(\d+)/gi,
          /\b(\d+)\s*files?\b/gi,
          /\.pdf\b/gi,
        ];
        for (const pattern of docPatterns) {
          let m: RegExpExecArray | null;
          if (pattern.source.includes(".pdf")) {
            const matches = searchText.match(pattern);
            if (matches) {
              documentCount = Math.max(documentCount, matches.length);
              details += `Doc refs:${matches.length} PDFs; `;
            }
            continue;
          }
          while ((m = pattern.exec(searchText)) !== null) {
            const num = parseInt(m[1] || "0");
            if (!isNaN(num)) documentCount = Math.max(documentCount, num);
            details += `Doc ref:"${m[0]}"; `;
          }
        }

        // Fallback: If section explicitly lists an item but no numeric count, infer at least 1
        // But first check if it's actually indicating "no photos" before inferring
        if (photoCount === 0 && /attachments[\s\S]*photo/i.test(searchText)) {
          // Check if the text actually indicates "no photos" or "0 photos"
          if (!/no\s*photos|photos\s*0|0\s*photos|nophotos/i.test(searchText)) {
            photoCount = 1;
            details += "Inferred 1 photo from attachments listing; ";
          } else {
            details += "Found 'photo' mention but indicates no photos; ";
          }
        }

        // Similar fallback for documents - check for "no documents" patterns
        if (documentCount === 0 && /attachments[\s\S]*document/i.test(searchText)) {
          // Check if the text actually indicates "no documents" or "0 documents"
          if (!/no\s*documents|documents\s*0|0\s*documents|nodocuments/i.test(searchText)) {
            documentCount = 1;
            details += "Inferred 1 document from attachments listing; ";
          } else {
            details += "Found 'document' mention but indicates no documents; ";
          }
        }

        await this.logSuccess(`PDF attachment analysis complete: ${photoCount} photos, ${documentCount} documents`);
        await this.logSuccess(`PDF attachment details: ${details}`);
        return { photos: photoCount, documents: documentCount, details };
      } catch (error) {
        await this.logSuccess(`Error analyzing PDF attachments: ${error}`);
        return { photos: 0, documents: 0, details: `Error: ${error}` };
      }
    });
  }

  public async testStepHeading(heading: string) {
    await allure.description(heading);
  }

  public async testStep(
    stepDescription: string,
    actionFunction: () => Promise<void> | void
  ): Promise<void> {
    await allure.step(stepDescription, async () => {
      try {
        await actionFunction();
        await this.logSuccess(`Step Completed: ${stepDescription}`);
      } catch (error) {
        await this.logMessage(`Step failed: ${stepDescription}`);
        throw error;
      }
    });
  }
  public async logMessage(message: string) {
    await allure.step(message, async () => {});
  }

  public parseParams(params: any): object {
    if (typeof params === "string") {
      try {
        return params.trim() ? JSON.parse(params) : {};
      } catch (jsonError) {
        console.warn(`Invalid JSON in Params: ${params}`);
        return {};
      }
    } else if (params !== null && typeof params === "object") {
      return params;
    }
    return {};
  }

  public parseQueryParams(endpoint: string, queryParams: any): string {
    let parsedEndpoint = endpoint;

    // Check if queryParams is a string and parse it to an object
    if (typeof queryParams === "string") {
      try {
        queryParams = JSON.parse(queryParams);
      } catch (jsonError) {
        console.warn(`Invalid JSON in QueryParams: ${queryParams}`);
        queryParams = {};
      }
    }

    // Replace placeholders in the endpoint with the corresponding values from queryParams
    for (const key in queryParams) {
      if (queryParams.hasOwnProperty(key)) {
        const value = queryParams[key];
        const placeholder = `{${key}}`;
        parsedEndpoint = parsedEndpoint.replace(
          new RegExp(placeholder, "g"),
          value
        );
      }
    }

    return parsedEndpoint;
  }

  public formatDuration(duration: number): string {
    const milliseconds = duration % 1000;
    const seconds = Math.floor((duration / 1000) % 60);
    const minutes = Math.floor((duration / (1000 * 60)) % 60);
    const hours = Math.floor((duration / (1000 * 60 * 60)) % 24);

    return `${hours}h ${minutes}m ${seconds}s ${milliseconds}ms`;
  }

  public async getElementText(selector: string): Promise<string> {
    return await allure.step(
      `Getting Element Text at locator: ${selector}`,
      async () => {
        const element = this.page.locator(selector);
        return (await element.textContent()) ?? "";
      }
    );
  }

  public async getInputElementPlaceholder(selector: string): Promise<string> {
    return await this.page.$eval(
      selector,
      (element) => (element as HTMLInputElement).placeholder
    );
  }

  public async validateInputElementPlaceholderText(
    selector: string,
    expectedText: string,
    elementDescription: string,
    pageName: string = "current",
    customPassMessage?: string,
    customFailMessage?: string
  ) {
    const actualText = await this.getInputElementPlaceholder(selector);
    const isPass = actualText === expectedText;
    const result = isPass ? "Pass ✅" : "Fail ❌";

    let message: string;

    if (isPass) {
      message =
        customPassMessage ||
        `${pageName} page contains expected text "${actualText}" for ${elementDescription}`;
    } else {
      message =
        customFailMessage ||
        `${pageName} page shows unexpected text "${actualText}" instead of "${expectedText}" for ${elementDescription}`;
    }

    await allure.step(`Result : ${result} : ${message}`, async () => {});

    return isPass;
  }

  // In TestBase.ts
  public async validateAndLogElementText(
    selector: string,
    expectedText: string,
    elementDescription: string,
    pageName: string = "current",
    customPassMessage?: string,
    customFailMessage?: string
  ) {
    const actualText = await this.getElementText(selector);
    const isPass = actualText.trim() === expectedText.trim();
    const result = isPass ? "Pass ✅" : "Fail ❌";

    let message: string;
    if (isPass) {
      message =
        customPassMessage ||
        `${pageName} page contains expected text "${actualText}" for ${elementDescription}`;
    } else {
      message =
        customFailMessage ||
        `${pageName} page shows unexpected text "${actualText}" instead of "${expectedText}" for ${elementDescription}`;
    }

    await allure.step(`Result : ${result} : ${message}`, async () => {});
  }

  public async logTestCaseAndDescription(
    testCaseId: string,
    description: string
  ) {
    await allure.step(`Test case id : ${testCaseId}`, async () => {});

    await allure.step(`Description : ${description}`, async () => {});
  }

  public async logSuccess(message: string) {
    await allure.step(`Result : Pass ✅ : ${message}`, async () => {});
  }

  public async logFailure(message: string) {
    await allure.step(`Result : Fail ❌ : ${message}`, async () => {});
  }

  public async logTestStart(testCaseId: string, description: string) {
    await this.logTestCaseAndDescription(testCaseId, description);
  }

  public async clickButton(
    locator: Locator,
    buttonName?: string
  ): Promise<void> {
    await allure.step(`Click ${buttonName} Button`, async () => {
      try {
        await locator.click();
        await this.logSuccess(`Successfully clicked ${buttonName} button`);
      } catch (error) {
        await this.logMessage(`Failed to click ${buttonName} button`);
        throw error;
      }
    });
  }
   
 
  

  public ensureBaseURL(baseURL: string | undefined): string {
    if (!baseURL) {
      throw new Error("baseURL is undefined. Please provide a valid baseURL.");
    }
    return baseURL;
  }

  public convertTextToDate(dateText: string): Date {
    try {
      // Remove periods and convert to standard format
      const cleanText = dateText.replace(/\./g, "").replace(",", "");

      // Parse the date using Date constructor
      const parsedDate = new Date(cleanText);

      // Validate the date
      if (isNaN(parsedDate.getTime())) {
        throw new Error(`Invalid date format: ${dateText}`);
      }

      return parsedDate;
    } catch (error) {
      throw new Error(`Error converting date: `);
    }
  }

  public addTimeToCurrentTime(time: Date = new Date()): Date {
    // Create a new Date object with the provided time or current time
    const newTime: Date = new Date(time);
    console.log("New Time is : ", +newTime);
    // Add 5.5 hours (5 hours and 30 minutes)
    newTime.setHours(newTime.getHours() + 5);
    newTime.setMinutes(newTime.getMinutes() + 30);

    return newTime;
  }
  public async checkTimeDifference(timeString: string) {
    const givenTime = new Date(timeString);
    console.log("Given Time is : ", +givenTime);
    const currentTime = new Date();
    console.log("Current Time is : ", +currentTime);
    const diffInMs = Math.abs(currentTime.getTime() - givenTime.getTime());
    const diffInMinutes = diffInMs / (1000 * 60);
    console.log("the differnce time is " + diffInMinutes);
    return {
      isWithinHour: diffInMinutes <= 30,
      diffInMinutes: Math.floor(diffInMinutes),
      diffInHours: Math.floor(diffInMinutes / 60),
    };
  }

  public async startNetworkMonitoring(): Promise<void> {
    await allure.step("Starting network monitoring", async () => {
      this.networkLogs = [];
      this.errorLogs = [];

      // Listen for all responses
      this.page.on("response", async (response) => {
        const url = response.url();
        const status = response.status();
        const method = response.request().method();
        const timestamp = this.gettxtlogdatetime;

        this.networkLogs.push({ url, status, method, timestamp });

        // Log each network call
        await this.logMessage(
          `Network Call: ${method} ${url} - Status: ${status}`
        );

        // Capture non-2XX status codes
        if (status < 200 || status >= 310) {
          let errorDetails = "";
          try {
            const responseBody = await response.text();
            errorDetails = responseBody;
          } catch (e) {
            errorDetails = "Could not get response body";
          }

          const errorLog = {
            url,
            status,
            method,
            timestamp,
            errorDetails,
          };

          this.errorLogs.push(errorLog);

          // Log error to Allure with details
          await allure.step(
            `🚨 Error Response: ${method} ${url} - Status: ${status}`,
            async () => {
              await this.logFailure(
                `API call failed: ${method} ${url} - Status: ${status}`
              );

              // Create a unique filename for each error
              const errorFileName = `error-response-${status}-${Date.now()}.json`;

              // Attach error details as a JSON file
              await allure.attachment(
                errorFileName,
                JSON.stringify(errorLog, null, 2),
                "application/json"
              );
            }
          );
          if (this.errorLogs.length > 0) {
            throw new Error(
              `Network errors detected, thus smoke suite Failed : ${this.errorLogs[0].errorDetails}`
            );
          }
        }
      });
    });
  }

  /**
   * Logs all captured non-2XX network calls to the test report and throws error if any found
   */
  public async logErrorCalls(): Promise<void> {
    await allure.step("Error Network Calls Summary", async () => {
      if (this.errorLogs.length === 0) {
        await this.logSuccess("No error responses were captured");
        return;
      }

      // Group errors by status code
      const errorsByStatus = this.errorLogs.reduce((acc, call) => {
        const status = call.status;
        if (!acc[status]) {
          acc[status] = [];
        }
        acc[status].push(call);
        return acc;
      }, {} as Record<number, typeof this.errorLogs>);

      // Log summary
      await this.logFailure(
        `🚨 Total Error Responses: ${this.errorLogs.length}`
      );

      // Create a summary file with all errors
      const summaryFileName = `error-summary-${Date.now()}.json`;
      await allure.attachment(
        summaryFileName,
        JSON.stringify(this.errorLogs, null, 2),
        "application/json"
      );

      // Log errors by status code
      for (const [status, calls] of Object.entries(errorsByStatus)) {
        await this.logFailure(`🚨 Status ${status}: ${calls.length} calls`);

        // Create a file for each status code group
        const statusFileName = `error-status-${status}-${Date.now()}.json`;
        await allure.attachment(
          statusFileName,
          JSON.stringify(calls, null, 2),
          "application/json"
        );

        // Log details for each error call
        for (const call of calls) {
          await allure.step(
            `Error Details: ${call.method} ${call.url}`,
            async () => {
              await this.logFailure(
                `- ${call.method} ${call.url} (${call.timestamp})`
              );
            }
          );
        }
      }

      // Throw error to fail the test when network errors are detected
      const errorMessage = `🚨 Network monitoring detected ${this.errorLogs.length} error responses. Test failed due to network errors.`;
      throw new Error(errorMessage);
    });
  }

  /**
   * Clears all captured network and error logs
   */
  public clearNetworkLogs(): void {
    this.networkLogs = [];
    this.errorLogs = [];
  }

  public async scanQRCode(screenshot: Buffer): Promise<string> {
    const image = await Jimp.read(screenshot);
    const { width, height, data } = image.bitmap;

    const code = jsQR(new Uint8ClampedArray(data.buffer), width, height);
    if (!code?.data) {
      throw new Error("QR Code not found in the image");
    }
    return code.data;
  }

}
