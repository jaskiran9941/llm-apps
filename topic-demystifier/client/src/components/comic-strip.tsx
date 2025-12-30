import { useState } from "react";
import { ChevronLeft, ChevronRight, Download } from "lucide-react";
import { jsPDF } from "jspdf";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import type { ComicPanel } from "@shared/schema";

interface ComicStripProps {
  panels: ComicPanel[];
  topic?: string;
  summary?: string;
}

export function ComicStrip({ panels, topic, summary }: ComicStripProps) {
  const [activeIndex, setActiveIndex] = useState(0);
  const [isExporting, setIsExporting] = useState(false);

  const goToPrevious = () => {
    setActiveIndex((prev) => (prev > 0 ? prev - 1 : panels.length - 1));
  };

  const goToNext = () => {
    setActiveIndex((prev) => (prev < panels.length - 1 ? prev + 1 : 0));
  };

  const exportToPdf = async () => {
    setIsExporting(true);
    try {
      const pdf = new jsPDF({
        orientation: "landscape",
        unit: "mm",
        format: "a4",
      });

      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const margin = 15;
      const contentWidth = pageWidth - margin * 2;

      pdf.setFontSize(24);
      pdf.setFont("helvetica", "bold");
      const topicText = topic || "Comic Explanation";
      pdf.text(topicText, pageWidth / 2, margin + 10, { align: "center" });

      if (summary) {
        pdf.setFontSize(11);
        pdf.setFont("helvetica", "normal");
        const summaryLines = pdf.splitTextToSize(summary, contentWidth - 20);
        pdf.text(summaryLines, pageWidth / 2, margin + 20, { align: "center" });
      }

      const panelsPerRow = 2;
      const rowsPerPage = 2;
      const panelsPerPage = panelsPerRow * rowsPerPage;
      const panelWidth = (contentWidth - 10) / panelsPerRow;
      const panelHeight = 70;
      const startY = margin + (summary ? 40 : 25);
      const subsequentPageStartY = margin + 15;

      for (let i = 0; i < panels.length; i++) {
        const panel = panels[i];
        const col = i % panelsPerRow;
        const pageIndex = Math.floor(i / panelsPerPage);
        const indexOnPage = i % panelsPerPage;
        const rowOnPage = Math.floor(indexOnPage / panelsPerRow);

        if (i > 0 && indexOnPage === 0) {
          pdf.addPage();
        }

        const x = margin + col * (panelWidth + 10);
        const baseY = pageIndex === 0 ? startY : subsequentPageStartY;
        const y = baseY + rowOnPage * (panelHeight + 10);

        pdf.setDrawColor(200, 200, 200);
        pdf.setFillColor(250, 250, 250);
        pdf.roundedRect(x, y, panelWidth, panelHeight, 3, 3, "FD");

        pdf.setFontSize(10);
        pdf.setFont("helvetica", "bold");
        pdf.setFillColor(100, 100, 255);
        pdf.roundedRect(x + 3, y + 3, 22, 6, 2, 2, "F");
        pdf.setTextColor(255, 255, 255);
        pdf.text(`Panel ${i + 1}`, x + 5, y + 7);
        pdf.setTextColor(0, 0, 0);

        const imageUrl = panel.imageBase64 || panel.imageUrl;
        if (imageUrl) {
          try {
            const imgWidth = panelWidth - 10;
            const imgHeight = 35;
            pdf.addImage(imageUrl, "PNG", x + 5, y + 12, imgWidth, imgHeight);
          } catch (error) {
            pdf.setFontSize(20);
            pdf.setTextColor(200, 200, 200);
            pdf.text(`${i + 1}`, x + panelWidth / 2, y + 30, { align: "center" });
            pdf.setTextColor(0, 0, 0);
          }
        } else {
          pdf.setFontSize(20);
          pdf.setTextColor(200, 200, 200);
          pdf.text(`${i + 1}`, x + panelWidth / 2, y + 30, { align: "center" });
          pdf.setTextColor(0, 0, 0);
        }

        pdf.setFontSize(11);
        pdf.setFont("helvetica", "bold");
        const titleLines = pdf.splitTextToSize(panel.title, panelWidth - 10);
        pdf.text(titleLines.slice(0, 1), x + 5, y + 52);

        if (panel.speechBubble) {
          pdf.setFontSize(9);
          pdf.setFont("helvetica", "italic");
          const speechLines = pdf.splitTextToSize(`"${panel.speechBubble}"`, panelWidth - 10);
          pdf.text(speechLines.slice(0, 2), x + 5, y + 58);
        }

        pdf.setFontSize(8);
        pdf.setFont("helvetica", "normal");
        const descLines = pdf.splitTextToSize(panel.description, panelWidth - 10);
        pdf.text(descLines.slice(0, 2), x + 5, y + 65);
      }

      const filename = topic ? `${topic.replace(/[^a-z0-9]/gi, "_").toLowerCase()}_comic.pdf` : "comic_explanation.pdf";
      pdf.save(filename);
    } catch (error) {
      console.error("Failed to export PDF:", error);
    } finally {
      setIsExporting(false);
    }
  };

  if (panels.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-muted-foreground">
        No comic panels available
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <ScrollArea className="w-full">
        <div className="flex gap-6 pb-4">
          {panels.map((panel, index) => (
            <ComicPanelCard
              key={panel.id}
              panel={panel}
              index={index}
              isActive={index === activeIndex}
              onClick={() => setActiveIndex(index)}
            />
          ))}
        </div>
        <ScrollBar orientation="horizontal" />
      </ScrollArea>

      <div className="flex items-center justify-center gap-4">
        <Button
          variant="outline"
          size="icon"
          onClick={goToPrevious}
          data-testid="button-comic-prev"
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>

        <div className="flex gap-2">
          {panels.map((_, index) => (
            <button
              key={index}
              onClick={() => setActiveIndex(index)}
              className={`h-2.5 w-2.5 rounded-full transition-colors ${
                index === activeIndex ? "bg-primary" : "bg-muted"
              }`}
              data-testid={`button-comic-dot-${index}`}
            />
          ))}
        </div>

        <Button
          variant="outline"
          size="icon"
          onClick={goToNext}
          data-testid="button-comic-next"
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>

      <div className="flex justify-center">
        <Button
          variant="outline"
          onClick={exportToPdf}
          disabled={isExporting}
          data-testid="button-export-pdf"
        >
          {isExporting ? (
            <span className="flex items-center gap-2">
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
              Exporting...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <Download className="h-4 w-4" />
              Export to PDF
            </span>
          )}
        </Button>
      </div>
    </div>
  );
}

interface ComicPanelCardProps {
  panel: ComicPanel;
  index: number;
  isActive: boolean;
  onClick: () => void;
}

function ComicPanelCard({ panel, index, isActive, onClick }: ComicPanelCardProps) {
  const imageUrl = panel.imageBase64 || panel.imageUrl || null;

  return (
    <Card
      onClick={onClick}
      className={`relative flex-shrink-0 w-72 md:w-80 cursor-pointer transition-all duration-200 overflow-visible ${
        isActive ? "ring-2 ring-primary ring-offset-2 ring-offset-background" : ""
      }`}
      data-testid={`card-comic-panel-${panel.id}`}
    >
      <div className="aspect-[4/3] relative bg-gradient-to-br from-primary/5 to-accent/10 overflow-hidden rounded-t-xl">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={panel.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="font-display text-6xl font-bold text-primary/20">
              {index + 1}
            </span>
          </div>
        )}

        <div className="absolute top-3 left-3 bg-primary text-primary-foreground text-xs font-bold px-2 py-1 rounded-full">
          Panel {index + 1}
        </div>

        {panel.speechBubble && (
          <div className="absolute bottom-3 right-3 left-3 bg-white dark:bg-gray-900 rounded-2xl px-4 py-3 shadow-lg">
            <div className="absolute -bottom-2 right-8 w-4 h-4 bg-white dark:bg-gray-900 rotate-45 transform" />
            <p className="text-sm font-medium relative z-10 text-gray-900 dark:text-gray-100">
              {panel.speechBubble}
            </p>
          </div>
        )}
      </div>

      <div className="p-4 space-y-2">
        <h4 className="font-display font-bold text-base line-clamp-1">{panel.title}</h4>
        <p className="text-sm text-muted-foreground line-clamp-2">{panel.description}</p>
      </div>
    </Card>
  );
}
