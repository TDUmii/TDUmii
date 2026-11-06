"""Approved Bridge sprite rig and animation timing."""
from .core import blink, build


def build_sprite():
    bridge_eyes = '<path d="M1019 521L1079 512L1087 570L1027 579Z M1170 499L1231 490L1239 548L1178 557Z"/>'
    # Head and antenna move together around the neck; torso and rays stay put.
    bridge_head = '<path d="M1065 200H1210V312L1328 310L1350 360L1390 360L1400 418L1450 418L1500 575L1469 600L1420 611L1420 651L1370 667L1303 650L1040 685L965 720L928 677L879 680L842 530L864 504L864 489L896 482L896 416L927 407L927 386L943 375L943 351L1100 327L1093 321L1065 328Z"/>'
    # Foreground torso uses original pixels and the actual slanted silver top.
    # It occludes the neck underlap, keeping the white chest continuous.
    bridge_torso = '<path d="M1040 685L1303 650L1307 677H1337V696H1361V741H1306V856H1070V812H1042V784H1018V710H1040Z"/>'
    return build('bridge', {'eyes': bridge_eyes, 'head': bridge_head, 'torso': bridge_torso, 'caret': '<rect x="516" y="643" width="100" height="32"/>'}, bridge_head + '<rect x="516" y="643" width="100" height="32"/>',
        (
            '<path d="M1005 650L1338 629L1355 704L1020 741Z" fill="#06101b"/>'
            '<g>'
            '<animateTransform attributeName="transform" type="rotate" values="0 1170 653;0 1170 653;-3 1170 653;-3 1170 653;1.5 1170 653;0 1170 653;0 1170 653" keyTimes="0;.20;.30;.48;.60;.69;1" dur="6.4s" repeatCount="indefinite"/>'
            '<use xlink:href="#PREFIXsource" clip-path="url(#PREFIXhead)"/>'
        ) + blink(bridge_eyes, 535) + '</g><use xlink:href="#PREFIXsource" clip-path="url(#PREFIXtorso)"/>' +
        (
            '<rect x="516" y="643" width="100" height="32" fill="#172330"/>'
            '<use xlink:href="#PREFIXsource" clip-path="url(#PREFIXcaret)">'
            '<animate attributeName="opacity" values="1;0;1" calcMode="discrete" dur="1.2s" repeatCount="indefinite"/>'
            '</use>\n'
            '<g fill="#9cf1aa">'
            '<path d="M532 552H571V569H532Z" opacity="0">'
            '<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.16;.72;1" calcMode="discrete" dur="4.8s" repeatCount="indefinite"/>'
            '</path>'
            '<path d="M585 552H626V569H585Z" opacity="0">'
            '<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.29;.72;1" calcMode="discrete" dur="4.8s" repeatCount="indefinite"/>'
            '</path>'
            '<path d="M640 552H681V569H640Z" opacity="0">'
            '<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.42;.72;1" calcMode="discrete" dur="4.8s" repeatCount="indefinite"/>'
            '</path>'
            '</g>\n'
        ), 6.4)
