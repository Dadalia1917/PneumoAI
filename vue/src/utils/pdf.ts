import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

export const htmlToPDF = async (htmlId: string, title: string = "报表", bgColor = "#fff") => {
    const originalDom = document.getElementById(htmlId) as HTMLElement;
    if (!originalDom) {
        console.error("未找到指定的 DOM 元素");
        return;
    }

    // 克隆原始 DOM，并移除可能导致滚动的样式
    const cloneDom = originalDom.cloneNode(true) as HTMLElement;
    cloneDom.style.overflow = 'visible';
    cloneDom.style.height = 'auto';
    cloneDom.style.position = 'absolute';
    cloneDom.style.top = '-9999px';
    document.body.appendChild(cloneDom);

    const A4Width = 595.28;
    const canvas = await html2canvas(cloneDom, {
        scale: 2,
        useCORS: true,
        backgroundColor: bgColor,
        scrollY: -window.scrollY
    });

    // 截图完成后移除克隆的 DOM
    document.body.removeChild(cloneDom);

    const imgWidth = A4Width;
    const imgHeight = (A4Width / canvas.width) * canvas.height;
    const pageData = canvas.toDataURL("image/jpeg", 1.0);

    const PDF = new jsPDF("p", 'pt', 'a4');
    PDF.addImage(pageData, "JPEG", 0, 0, imgWidth, imgHeight);
    PDF.save(title + ".pdf");
};
