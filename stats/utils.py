 
from django.http import HttpResponse 
from django.template.loader import get_template
# from xhtml2pdf import pisa
import xhtml2pdf.pisa as pisa 
from django.conf import settings


def render_to_pdf(template_src, context_dict={}):
     
    # find the template and render it
    template = get_template(template_src)
    html = template.render(context_dict)

    # create a django response and specify content_type as pdf 
    response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = f'attachment; filename="reservation-report.pdf"'
    
    # create a pdf 
    pdf_status = pisa.CreatePDF(html, dest=response )

    if pdf_status.err:
        return HttpResponse('Some errors were encountered')
    return response
