#include "wasm_wrapper.cc"
#include <fstream>
#include <iostream>

int main() {
    init_decompiler();

    // Read SLA file
    std::ifstream sla_file("Processors/ARM/data/languages/ARM7_le.sla", std::ios::binary);
    std::string sla_str((std::istreambuf_iterator<char>(sla_file)), std::istreambuf_iterator<char>());

    // Read PSPEC and CSPEC files
    std::ifstream pspec_file("Processors/ARM/data/languages/ARMt.pspec");
    std::string pspec_str((std::istreambuf_iterator<char>(pspec_file)), std::istreambuf_iterator<char>());

    std::ifstream cspec_file("Processors/ARM/data/languages/ARM.cspec");
    std::string cspec_str((std::istreambuf_iterator<char>(cspec_file)), std::istreambuf_iterator<char>());

    // Read binary file
    std::ifstream bin_file("testdata/libcodec2.so", std::ios::binary);
    std::string bin_str((std::istreambuf_iterator<char>(bin_file)), std::istreambuf_iterator<char>());

    std::string hex_str;
    for (unsigned char c : bin_str) {
        char buf[3];
        snprintf(buf, sizeof(buf), "%02x", c);
        hex_str += buf;
    }

    std::string image_xml = "<binaryimage arch=\"ARM:LE:32:v7\">\n"
                            "  <bytechunk space=\"ram\" offset=\"0x1000\">\n" +
                            hex_str + "\n"
                            "  </bytechunk>\n"
                            "</binaryimage>";

    char* result = get_symbols((const uint8_t*)sla_str.data(), sla_str.size(),
                               pspec_str.c_str(), cspec_str.c_str(),
                               image_xml.c_str());

    std::cout << "Symbols JSON:\n" << result << std::endl;
    free_string(result);
    return 0;
}
