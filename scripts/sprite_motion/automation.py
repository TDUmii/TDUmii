"""Approved Automation sprite rig and animation timing."""
from .core import blink, build


def build_sprite():
    auto_eyes = '<path d="M1035 413L1095 421L1088 479L1028 472Z M1180 430L1243 438L1235 498L1173 490Z"/>'
    # Trace the gear's own stepped outline, excluding adjacent replay arrows.
    gear = '<path d="M530 350H613V376H661V396L680 396L697 415V445L680 452H715V525L694 541V578L677 596H662V615H614V636H529V615H481V596H463L447 579V548L462 540H434L421 525V469L434 454H463L447 440V415L465 396H482V375H530Z"/>'
    cursor = '<rect x="219" y="514" width="249" height="403"/>'
    # The two original replay arrows take a small turn together, independently
    # from the faster inner gear, then settle into their original pose.
    replay_top = '<path d="M308 481V381H329V348H351V317H375V292H401V269H430V244H457V225H490V206H650V225H687V244H714V265H741V285H765L785 264H810V422L667 389L711 345L685 320H652V303H615V285H525V304H484V323H455V348H431V373H415V399H399V481Z"/>'
    replay_bottom = '<path d="M742 471H838V582H818V621H797V652H772V680H746V708H720V733H692V756H656V780H578L529 816L460 678L601 625L597 660H643V643H669V622H691V600H713V576H736V471Z"/>'
    return build('automation', {'eyes': auto_eyes, 'gear': gear, 'cursor': cursor, 'replay': replay_top + replay_bottom}, gear + cursor + replay_top + replay_bottom,
        blink(auto_eyes, 454, '3.4s') +
        (
            '<g>'
            '<animateTransform attributeName="transform" type="rotate" values="0 570 494;0 570 494;5 570 494;5 570 494;0 570 494;0 570 494" keyTimes="0;.12;.30;.48;.65;1" dur="4s" repeatCount="indefinite"/>'
            '<use xlink:href="#PREFIXsource" clip-path="url(#PREFIXreplay)"/>'
            '</g>\n'
            '<g>'
            '<animateTransform attributeName="transform" type="rotate" from="0 570 494" to="360 570 494" dur="8s" repeatCount="indefinite"/>'
            '<use xlink:href="#PREFIXsource" clip-path="url(#PREFIXgear)"/>'
            '</g>\n'
            '<g>'
            '<animateTransform attributeName="transform" type="translate" values="0 0;0 0;8 -8;0 0;0 0" keyTimes="0;.32;.38;.44;1" dur="2s" repeatCount="indefinite"/>'
            '<use xlink:href="#PREFIXsource" clip-path="url(#PREFIXcursor)"/>'
            '</g>\n'
            '<g fill="none" stroke="#ffbf3e" stroke-width="9" opacity="0">'
            '<path d="M245 488V463M203 510L184 491M281 501L300 482"/>'
            '<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;.34;.39;.52;1" dur="2s" repeatCount="indefinite"/>'
            '</g>\n'
            '<path d="M1182 159L1231 165L1225 209L1176 203Z" fill="#ff9b8f" opacity="0">'
            '<animate attributeName="opacity" values="0;0;.75;0;0" keyTimes="0;.42;.48;.57;1" dur="2s" repeatCount="indefinite"/>'
            '</path>'
        ), 8)
