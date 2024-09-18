from hl7apy.parser import parse_message, parse_segment, parse_segments, parse_fields, parse_component
from hl7apy.v2_4 import ST

class HL7Utill:
    message = """MSH|^~\&|HIS^^^WOWHIS&2.16.840.1.113883.3.3731.1.2.2.123456789.61&ISO|EJH^^^HIS&2.16.840.1.113883.3.3731.1.2.2.123456789&ISO|WOWRIS^^^WOWRIS&2.16.840.1.113883.3.3731.1.2.2.987654329.62&ISO|^^^RIS&2.16.840.1.113883.3.3731.1.2.2.987654329&ISO|20150919032300||ORU^R01|MSG963595321|T|2.3.1|||||||||
EVN|A28|20150919032300|||||
PID|1||115202339^^^MRNPID&2.16.840.1.113883.3.3731.1.2.2.XXXX.Y&ISO~100224145221044^^^NHID&2.16.840.1.113883.3.3731.1.1.100.1&ISO~1000577344^^^NID&2.16.840.1.113883.3.3731.1.2.2.XXXX.Y&ISO||Alshaibi^Omar^Mohammed^Taha||19810724|M|الشيبي^عمر^محمد^طه||Jeddah|SA|0555715514|||M|ISLM||||||Taif|||SA||SA|00000000000000|N
OBR|1||BAR101010101|^AUTO ANALIZADOR HEMATOLÓGICO 5 DIF Mythic 5Vet PRO||||01110621143134|||||^||||||||||||||||
OBX|1|NM|WBC||110.0|10^9/L|40.0-100.0|H|||F|||||||
OBX|2|NM|LYM||35.57|%|20.00-40.00||||F|||||||
OBX|3|NM|MON||5.84|%|3.00-8.00||||F|||||||
OBX|4|NM|NEU||57.37|%|50.00-70.00||||F|||||||
OBX|5|NM|EOS||1.14|%|0.50-5.00||||F|||||||
OBX|6|NM|BASO||0.08|%|0.00-1.00||||F|||||||
OBX|7|NM|LYM#||284.5|10^9/L|80.0-400.0||||F|||||||
OBX|8|NM|MON#||46.7|10^9/L|10.0-80.0||||F|||||||
OBX|9|NM|NEU#||458.9|10^9/L|200.0-700.0||||F|||||||
OBX|10|NM|EOS#||9.1|10^9/L|0.0-50.0||||F|||||||
OBX|11|NM|BASO#||0.6|10^9/L|0.0-10.0||||F|||||||
OBX|12|NM|RBC||4.49|10^12/L|3.50-5.50||||F|||||||
OBX|13|NM|HGB||0|g/L|0-1079738368|L|||F|||||||
OBX|14|NM|HCT||26.4|%|37.0-50.0|L|||F|||||||
OBX|15|NM|MCV||59.0|fL|80.0-100.0|L|||F|||||||
OBX|16|NM|MCH||24.0|pg|27.0-31.0|L|||F|||||||
OBX|17|NM|MCHC||0|g/L|0-1081344000|H|||F|||||||
OBX|18|NM|RDW_CV||16.1|%|11.5-14.5|H|||F||||||
OBX|19|NM|RDW_SD||45.0|fL|35.0-56.0||||F||||||
OBX|20|NM|PLT||0|10^9/L|0-1079574528|H|||F|||||||
OBX|21|NM|MPV||12.3|fL|7.0-11.0|H|||F|||||||
OBX|22|NM|PDW||14.7|fL|15.0-17.0|L|||F|||||||
OBX|23|NM|PCT||0.41|%|0.10-0.28|H|||F|||||||
OBX|24|NM|P_LCR||1.37|%|0.50-1.80||||F|||||||
OBX|25|ED|RBCHistogram||Mythic 5Vet PRO^Image^BMP^Base64^Qk32lgMAAA……
OBX|26|ED|PLTHistogram|Mythic 5Vet PRO^Image^BMP^Base64^Qk32lgMAAA……
OBX|27|ED|S0_S10DIFFScattergram||Mythic 5Vet PRO^Image^BMP^Base64^Qk32lgMAAA……
OBX|28|ED|S90_S90DDIFFScattergram||Mythic 5Vet PRO^Image^BMP^Base64^Qk32lgMAAA……"""

    def __init__(self):
        """
        Initializes the HL7Utill instance.

        This constructor calls the prepareMessageOptions method to 
        process the default HL7 message defined in the class.
        """
        self.prepareMessageOptions()
    
    @classmethod
    def prepareMessageOptions(cls, msg=None):
        """
        Prepares message options from the provided HL7 message.

        This method extracts segments and fields from an HL7 message,
        organizing them into a dictionary structure for easy access
        and manipulation. Each segment's fields are stored in a nested
        dictionary under the corresponding segment key.

        Args:
            msg (str): The HL7 message as a string. If not provided, 
                        the class's message attribute will be used.

        Returns:
            dict: A dictionary containing segments as keys and their 
                  corresponding fields as values. Each field is stored
                  as a key-value pair where the key is the field name 
                  and the value is a dictionary of its components.

        Example:
            options = HL7Utill.prepareMessageOptions("MSH|...|EVN|...")
            print(options['MSH'])
        """
        msg = cls.message if msg is None else msg  # Use cls attribute if no message is provided
        options = {}
        segments = cls.getDictSegments(msg)
        for index, (sKey, value) in enumerate(segments.items()):
            options[sKey] = {}
            fields = parse_segment(value).children
            for i, field in enumerate(fields):
                cDict = {}
                components = field.children
                for j, component in enumerate(components):
                    subComponentCounter = []
                    subComponents = component.children
                    for y, sc in enumerate(subComponents):
                        subComponentCounter.append(str(y + 1))
                    cDict[str(j + 1)] = subComponentCounter
                if field.name in options[sKey]:
                    options[sKey][field.name + '~' + str(i)] = cDict
                else:
                    options[sKey][field.name] = cDict
        return options

    @classmethod
    def getDictSegments(cls, msg):
        """
        Extracts segments from the given HL7 message.

        This method splits the message into lines, parses each line
        as a segment, and organizes them into a dictionary based on 
        segment names. Special handling is applied for MSH and EVN 
        segments.

        Args:
            msg (str): The HL7 message as a string.

        Returns:
            dict: A dictionary mapping segment names to their 
                  corresponding raw segment strings.

        Example:
            segments = HL7Utill.getDictSegments(message)
            print(segments['MSH'])
        """
        segments = {}
        for s in msg.splitlines():  # Ensure splitting by lines
            seg = parse_segment(s)
            if seg.name == "MSH" or seg.name == "EVN":
                segments[seg.name] = s
                continue
            segments[seg.name + '-' + str(seg.children[0].children[0].children[0].value.value)] = s
        return segments

    @classmethod
    def extractMetadata(cls , msh):
        """
        Extracts meta data from msh segment

        This method will return sender info , reciver info , message type

        Args: 
            msh : string

        Returns:
            dict : A dictionary mapping for sender and reciver and message type

        Exmaple:
            returning example : {"application_sender":{"name":"HIS" ,"oid":"2.16.840.1.113883.3.3731.1.2.2.123456789"}}
        """

        mshSeg = parse_segment(msh)
        
        """ ---------------------- Meta Data ---------------------- """
        sendingApplication = mshSeg.sending_application[0].children[1].value.split("&")
        sendingFacility = mshSeg.sending_facility[0].children[1].value.split("&")
        receivingApplication = mshSeg.receiving_application[0].children[1].value.split("&")
        receivingFacility = mshSeg.receiving_facility[0].children[0].value.split("&")
        
        """ ---------------------- Message Type  ---------------------- """
        messageType = mshSeg.message_type.value.split("^")

        return {
            "application_sender":{"name":sendingApplication[0] , "oid":sendingApplication[1]},
            "facility_sender":{"name":sendingFacility[0] , "oid":sendingFacility[1]},
            "application_receiver":{"name":receivingApplication[0] , "oid":receivingApplication[1]},
            "facility_receiver":{"name":receivingFacility[0] , "oid":receivingFacility[1]},
            "message_type":{"type":messageType[0] , "code":messageType[1]}
        }



    

# To run the utility
if __name__ == "__main__":
    HL7Utill()
