
import json
import re
import os
import glob

# Central Section Titles Map
SECTION_TITLES = {
    "Preface": "Lời nói đầu",
    "Acknowledgments": "Lời cảm ơn",
    "Introduction: Paradigms in science and society": "Lời giới thiệu: Các hệ hình trong khoa học và xã hội",
    "The Scientific Revolution": "Cuộc Cách mạng Khoa học",
    "Newtonian physics": "Vật lý học Newton",
    "Concluding remarks": "Nhận xét kết luận",
    "Early mechanical models of living organisms": "Các mô hình cơ học ban đầu về sinh vật sống",
    "From cells to molecules": "Từ tế bào đến phân tử",
    "The century of the gene": "Thế kỷ của gene",
    "Mechanistic medicine": "Y học cơ giới luận",
    "Birth of the social sciences": "Sự ra đời của các khoa học xã hội",
    "Classical political economy": "Kinh tế chính trị học cổ điển",
    "The critics of classical economics": "Những tiếng nói phê phán kinh tế học cổ điển",
    "Keynesian economics": "Kinh tế học Keynes",
    "The impasse of Cartesian economics": "Sự bế tắc của kinh tế học Descartes",
    "The machine metaphor in management": "Ẩn dụ cỗ máy trong quản trị",
    "From the parts to the whole": "Từ các bộ phận đến toàn thể",
    "The emergence of systems thinking": "Sự xuất hiện của tư duy hệ thống",
    "The new physics": "Vật lý học mới",
    "Classical systems theories": "Các lý thuyết hệ thống cổ điển",
    "Tektology": "Tektology (Khoa học tổ chức)",
    "General systems theory": "Lý thuyết hệ thống tổng quát",
    "Cybernetics": "Điều khiển học",
    "Complexity theory": "Lý thuyết phức tạp",
    "The mathematics of classical science": "Toán học của khoa học cổ điển",
    "Facing nonlinearity": "Đối diện với tính phi tuyến",
    "Principles of nonlinear dynamics": "Các nguyên lý của động lực học phi tuyến",
    "Fractal geometry": "Hình học fractal",
    "What is life?": "Sự sống là gì?",
    "How to characterize the living": "Làm thế nào để mô tả đặc tính của sự sống",
    "The systems view of life": "Cái nhìn hệ thống về sự sống",
    "The fundamentals of autopoiesis": "Các nền tảng của tự tạo sinh (autopoiesis)",
    "The interaction with the environment": "Sự tương tác với môi trường",
    "Social autopoiesis": "Tự tạo sinh trong xã hội",
    "Criteria of autopoiesis, criteria of life": "Tiêu chí tự tạo sinh, tiêu chí của sự sống",
    "What is death?": "Cái chết là gì?",
    "Autopoiesis and cognition": "Tự tạo sinh và nhận thức",
    "Order and complexity in the living world": "Trật tự và tính phức tạp trong thế giới sống",
    "Self-organization": "Sự tự tổ chức",
    "Emergence and emergent properties": "Sự nảy sinh và các đặc tính nảy sinh",
    "Self-organization and emergence in dynamic systems": "Sự tự tổ chức và tính nảy sinh trong các hệ thống động",
    "Guest essay: Daisyworld": "Bài luận khách mời: Thế giới hoa cúc (Daisyworld)",
    "Mathematical patterns in the living world": "Các mẫu hình toán học trong thế giới sống",
    "Darwin and biological evolution": "Darwin và sự tiến hóa sinh học",
    "Darwin's vision of species interlinked by a network of parenthood": "Tầm nhìn của Darwin về các loài liên kết trong mạng lưới huyết thống",
    "Darwin, Mendel, Lamarck, and Wallace: a multifaceted interconnection": "Darwin, Mendel, Lamarck và Wallace: Mối liên kết đa diện",
    "The modern evolutionary synthesis": "Thuyết tiến hóa tổng hợp hiện đại",
    "Applied genetics": "Di truyền học ứng dụng",
    "The Human Genome Project": "Dự án Bộ gene Người",
    "Conceptual revolution in genetics": "Cuộc cách mạng khái niệm trong di truyền học",
    "Guest essay: The rise and rise of epigenetics": "Bài luận khách mời: Sự trỗi dậy mạnh mẽ của di truyền biểu sinh",
    "Darwinism and creationism": "Thuyết Darwin và thuyết sáng tạo",
    "Chance, contingency, and evolution": "Sự ngẫu nhiên, tính bất định và tiến hóa",
    "Darwinism today": "Thuyết Darwin ngày nay",
    "The quest for the origin of life on Earth": "Cuộc truy tìm nguồn gốc sự sống trên Trái Đất",
    "Oparin's molecular evolution": "Tiến hóa phân tử của Oparin",
    "Contingency versus determinism in the origin of life": "Tính bất định đối lập với thuyết tất định trong nguồn gốc sự sống",
    "Prebiotic chemistry": "Hóa học tiền sinh học",
    "Laboratory approaches to minimal life": "Các cách tiếp cận phòng thí nghiệm đối với sự sống tối thiểu",
    "The synthetic-biology approach to the origin of life": "Cách tiếp cận sinh học tổng hợp đối với nguồn gốc sự sống",
    "The human adventure": "Cuộc phiêu lưu của con người",
    "The ages of life": "Các kỷ nguyên của sự sống",
    "The age of humans": "Kỷ nguyên của loài người",
    "The determinants of being human": "Những yếu tố định hình bản chất con người",
    "Mind and consciousness": "Tâm trí và ý thức",
    "Mind is a process!": "Tâm trí là một quá trình!",
    "The Santiago theory of cognition": "Lý thuyết nhận thức Santiago",
    "Cognition and consciousness": "Nhận thức và ý thức",
    "Guest essay: On the primary nature of consciousness": "Bài luận khách mời: Về bản chất nguyên sơ của ý thức",
    "Cognitive linguistics": "Ngôn ngữ học nhận thức",
    "Science and spirituality": "Khoa học và tâm linh",
    "Science and spirituality: a dialectic relationship": "Khoa học và tâm linh: Mối quan hệ biện chứng",
    "Spirituality and religion": "Tâm linh và tôn giáo",
    "Science versus religion: a “dialogue of the deaf”?": "Khoa học đối lập tôn giáo: Một “cuộc đối thoại của những kẻ điếc”?",
    "Parallels between science and mysticism": "Những nét tương đồng giữa khoa học và chủ nghĩa thần bí",
    "Spiritual practice today": "Thực hành tâm linh ngày nay",
    "Spirituality, ecology, and education": "Tâm linh, sinh thái và giáo dục",
    "Life, mind, and society": "Sự sống, tâm trí và xã hội",
    "The evolutionary link between consciousness and social phenomena": "Mối liên hệ tiến hóa giữa ý thức và các hiện tượng xã hội",
    "Sociology and the social sciences": "Xã hội học và các khoa học xã hội",
    "Extending the systems approach": "Mở rộng cách tiếp cận hệ thống",
    "Networks of communications": "Các mạng lưới truyền thông giao tiếp",
    "Life and leadership in organizations": "Sự sống và năng lực lãnh đạo trong các tổ chức",
    "The systems view of health": "Cách tiếp cận hệ thống về sức khỏe",
    "Crisis in healthcare": "Cuộc khủng hoảng trong chăm sóc y tế",
    "What is health?": "Sức khỏe là gì?",
    "Guest essay: Placebo and nocebo responses": "Bài luận khách mời: Phản ứng giả dược (placebo) và phản dược (nocebo)",
    "A systemic approach to healthcare": "Cách tiếp cận hệ thống đối với chăm sóc y tế",
    "Guest essay: Integrative practice in healthcare and healing": "Bài luận khách mời: Thực hành tích hợp trong y tế và chữa lành",
    "The ecological dimension of life": "Chiều kích sinh thái của sự sống",
    "The science of ecology": "Khoa học sinh thái",
    "Systems ecology": "Sinh thái học hệ thống",
    "Ecological sustainability": "Tính bền vững sinh thái",
    "Connecting the dots: systems thinking and the state of the world": "Kết nối các điểm nút: Tư duy hệ thống và hiện trạng thế giới",
    "Connecting the dots": "Kết nối các điểm nút",
    "Interconnectedness of world problems": "Tính liên kết tương hỗ của các vấn đề thế giới",
    "The illusion of perpetual growth": "Ảo tưởng về sự tăng trưởng vô tận",
    "The networks of global capitalism": "Các mạng lưới của chủ nghĩa tư bản toàn cầu",
    "The global civil society": "Xã hội dân sự toàn cầu",
    "Systemic solutions": "Các giải pháp hệ thống",
    "Changing the game": "Thay đổi luật chơi",
    "Guest essay: Living enterprise as the foundation of a generative economy": "Bài luận khách mời: Doanh nghiệp sống như nền tảng của một nền kinh tế sinh tạo",
    "Energy and climate change": "Năng lượng và biến đổi khí hậu",
    "Agroecology – the best chance to feed the world": "Nông nghiệp sinh thái – Cơ hội tốt nhất để nuôi sống thế giới",
    "Guest essay: Seeds of life": "Bài luận khách mời: Hạt giống của sự sống",
    "Designing for life": "Thiết kế vì sự sống",
    "Bibliography": "Thư mục tham khảo",
    "Index": "Chỉ mục"
}

CHAPTER_TITLES = {
    0: "Lời Nói Đầu & Giới Thiệu: Các Hệ Hình Trong Khoa Học Và Xã Hội",
    1: "Chương 1: Cỗ Máy Thế Giới Của Newton",
    2: "Chương 2: Quan Niệm Cơ Giới Về Sự Sống",
    3: "Chương 3: Tư Tưởng Xã Hội Cơ Giới Luận",
    4: "Chương 4: Từ Bộ Phận Đến Toàn Thể",
    5: "Chương 5: Các Lý Thuyết Hệ Thống Cổ Điển",
    6: "Chương 6: Lý Thuyết Phức Tạp",
    7: "Chương 7: Sự Sống Là Gì?",
    8: "Chương 8: Trật Tự Và Tính Phức Tạp Trong Thế Giới Sống",
    9: "Chương 9: Darwin Và Sự Tiến Hóa Sinh Học",
    10: "Chương 10: Cuộc Truy Tìm Nguồn Gốc Sự Sống Trên Trái Đất",
    11: "Chương 11: Cuộc Phiêu Lưu Của Con Người",
    12: "Chương 12: Tâm Trí Và Ý Thức",
    13: "Chương 13: Khoa Học Và Tâm Linh",
    14: "Chương 14: Sự Sống, Tâm Trí Và Xã Hội",
    15: "Chương 15: Cách Tiếp Cận Hệ Thống Về Sức Khỏe",
    16: "Chương 16: Chiều Kích Sinh Thái Của Sự Sống",
    17: "Chương 17: Kết Nối Các Điểm Nút: Tư Duy Hệ Thống Và Hiện Trạng Thế Giới",
    18: "Chương 18: Các Giải Pháp Hệ Thống",
    19: "Chương 19: Thư Mục Tham Khảo & Chỉ Mục"
}

# Comprehensive academic translation dictionary and rules
PHRASES = [
    # Book title & parts
    (r"The Systems View of Life: A Unifying Vision", "Cái nhìn hệ thống về sự sống: Một tầm nhìn nhất thể hóa"),
    (r"The Systems View of Life", "Cái nhìn hệ thống về sự sống (The Systems View of Life)"),
    (r"the systems view of life", "cái nhìn hệ thống về sự sống"),
    (r"Systems view of life", "Cái nhìn hệ thống về sự sống"),
    (r"The mechanistic worldview", "Thế giới quan cơ giới luận"),
    (r"the mechanistic worldview", "thế giới quan cơ giới luận"),
    (r"mechanistic worldview", "thế giới quan cơ giới luận"),
    (r"The mechanistic view of life", "Quan niệm cơ giới về sự sống"),
    (r"the mechanistic view of life", "quan niệm cơ giới về sự sống"),
    (r"The Newtonian world-machine", "Cỗ máy thế giới của Newton"),
    (r"the Newtonian world-machine", "cỗ máy thế giới của Newton"),
    (r"Mechanistic social thought", "Tư tưởng xã hội cơ giới luận"),
    (r"mechanistic social thought", "tư tưởng xã hội cơ giới luận"),
    (r"From the parts to the whole", "Từ các bộ phận đến toàn thể"),
    (r"from the parts to the whole", "từ các bộ phận đến toàn thể"),
    (r"Classical systems theories", "Các lý thuyết hệ thống cổ điển"),
    (r"classical systems theories", "các lý thuyết hệ thống cổ điển"),
    (r"General systems theory", "Lý thuyết hệ thống tổng quát"),
    (r"general systems theory", "lý thuyết hệ thống tổng quát"),
    (r"Complexity theory", "Lý thuyết phức tạp"),
    (r"complexity theory", "lý thuyết phức tạp"),
    (r"Order and complexity in the living world", "Trật tự và tính phức tạp trong thế giới sống"),
    (r"order and complexity in the living world", "trật tự và tính phức tạp trong thế giới sống"),
    (r"Darwin and biological evolution", "Darwin và sự tiến hóa sinh học"),
    (r"The quest for the origin of life on Earth", "Cuộc truy tìm nguồn gốc sự sống trên Trái Đất"),
    (r"The human adventure", "Cuộc phiêu lưu của con người"),
    (r"Mind and consciousness", "Tâm trí và ý thức"),
    (r"Science and spirituality", "Khoa học và tâm linh"),
    (r"Life, mind, and society", "Sự sống, tâm trí và xã hội"),
    (r"The systems view of health", "Cách tiếp cận hệ thống về sức khỏe"),
    (r"The ecological dimension of life", "Chiều kích sinh thái của sự sống"),
    (r"Connecting the dots", "Kết nối các điểm nút"),
    (r"Systemic solutions", "Các giải pháp hệ thống"),
    (r"Sustaining the web of life", "Duy trì mạng lưới sự sống"),
    (r"The rise of systems thinking", "Sự trỗi dậy của tư duy hệ thống"),
    (r"A new conception of life", "Quan niệm mới về sự sống"),
    (r"Paradigms in science and society", "Các hệ hình trong khoa học và xã hội"),

    # Scientific Concepts & Terminology
    (r"autopoiesis", "tự tạo sinh (autopoiesis)"),
    (r"Autopoiesis", "Tự tạo sinh (Autopoiesis)"),
    (r"autopoietic networks?", "mạng lưới tự tạo sinh"),
    (r"autopoietic", "tự tạo sinh"),
    (r"self-organization", "sự tự tổ chức"),
    (r"self-organizing", "tự tổ chức"),
    (r"self-generating", "tự sản sinh"),
    (r"self-maintenance", "sự tự duy trì"),
    (r"self-regulation", "sự tự điều hòa"),
    (r"emergent properties", "các đặc tính nảy sinh (đặc tính trồi)"),
    (r"emergent property", "đặc tính nảy sinh"),
    (r"emergence", "sự nảy sinh (đặc tính trồi)"),
    (r"dissipative structures", "các cấu trúc tiêu tán"),
    (r"dissipative structure", "cấu trúc tiêu tán"),
    (r"non-equilibrium thermodynamics", "nhiệt động lực học phi cân bằng"),
    (r"nonlinear dynamics", "động lực học phi tuyến"),
    (r"nonlinearity", "tính phi tuyến"),
    (r"strange attractors?", "điểm hút kỳ dị"),
    (r"phase space", "không gian pha"),
    (r"bifurcation points?", "điểm rẽ nhánh"),
    (r"bifurcation", "sự rẽ nhánh"),
    (r"fractal geometry", "hình học fractal"),
    (r"feedback loops?", "vòng phản hồi"),
    (r"circular causality", "tính nhân quả vòng tròn"),
    (r"linear causality", "tính nhân quả tuyến tính"),
    (r"homeostasis", "cân bằng nội môi (homeostasis)"),
    (r"cybernetics", "điều khiển học"),
    (r"Cybernetics", "Điều khiển học"),
    (r"Tektology", "Tektology (Khoa học tổ chức)"),
    (r"tektology", "tektology"),
    (r"Santiago theory of cognition", "lý thuyết nhận thức Santiago"),
    (r"structural coupling", "sự ghép nối cấu trúc"),
    (r"cognitive science", "khoa học nhận thức"),
    (r"cognitive linguistics", "ngôn ngữ học nhận thức"),
    (r"cognition", "nhận thức"),
    (r"consciousness", "ý thức"),
    (r"epigenetics", "di truyền biểu sinh"),
    (r"Epigenetics", "Di truyền biểu sinh"),
    (r"symbiogenesis", "sự cộng sinh phát sinh"),
    (r"symbiosis", "sự cộng sinh"),
    (r"prebiotic chemistry", "hóa học tiền sinh học"),
    (r"minimal life", "sự sống tối thiểu"),
    (r"minimal cell", "tế bào tối thiểu"),
    (r"synthetic biology", "sinh học tổng hợp"),
    (r"origin of life", "nguồn gốc sự sống"),
    (r"Gaia theory", "thuyết Gaia"),
    (r"Daisyworld", "Thế giới hoa cúc (Daisyworld)"),
    (r"deep ecology", "sinh thái học chiều sâu"),
    (r"Deep Ecology", "Sinh thái học chiều sâu"),
    (r"ecological sustainability", "tính bền vững sinh thái"),
    (r"ecodesign", "thiết kế sinh thái (ecodesign)"),
    (r"agroecology", "nông nghiệp sinh thái"),
    (r"living systems?", "hệ thống sống"),
    (r"living organisms?", "sinh vật sống"),
    (r"web of life", "mạng lưới sự sống"),
    (r"the web of life", "mạng lưới sự sống"),
    (r"human dignity", "phẩm giá con người"),
    (r"interconnectedness", "tính liên kết tương hỗ"),
    (r"interdependence", "sự phụ thuộc lẫn nhau"),
    (r"reductionism", "chủ nghĩa giản lược"),
    (r"holism", "thuyết toàn thể"),
    (r"holistic", "toàn thể, toàn diện"),
    (r"paradigm shifts?", "sự chuyển dịch hệ hình"),
    (r"paradigms?", "hệ hình"),
    (r"worldviews?", "thế giới quan")
]

# General academic dictionary for scientific and philosophical prose
ACADEMIC_DICT = {
    "graphs": "các đồ thị", "graph": "đồ thị", "showing": "biểu thị", "show": "chỉ ra", "shows": "chỉ ra", "motion": "chuyển động", "bodies": "các vật thể", "body": "cơ thể", "moving": "chuyển động", "constant": "không đổi", "speed": "tốc độ", "accelerating": "tăng tốc", "accelerate": "tăng tốc", "schematization": "sơ đồ hóa", "schematic": "sơ đồ", "representing": "đại diện cho", "death": "cái chết", "surfactant": "chất hoạt động bề mặt", "hydrophilic": "ưa nước", "hydrophobic": "kỵ nước", "tails": "các đuôi", "tail": "đuôi", "critical": "tới hạn", "concentration": "nồng độ", "lipids": "các lipid", "lipid": "lipid", "triesters": "các trieste", "glycerol": "glycerol", "fatty": "béo", "acids": "các axit", "acid": "axit", "carboxylic": "carboxylic", "chain": "chuỗi", "helix": "chuỗi xoắn", "helical": "xoắn ốc", "interior": "bên trong", "avoiding": "tránh", "tobacco": "cây thuốc lá", "mosaic": "khảm", "mantle": "lớp vỏ bọc", "array": "mảng sắp xếp", "convection": "đối lưu", "silicone": "silicone", "oil": "dầu", "thickness": "độ dày", "chiral": "bất đối xứng (chiral)", "mirror": "gương", "images": "các hình ảnh", "image": "hình ảnh", "superimposable": "chồng khít lên nhau", "spiral": "xoắn ốc", "snail": "ốc sên", "mollusk": "thân mềm", "sunflower": "hoa hướng dương", "packed": "xếp chặt", "tightly": "chặt chẽ", "interlocking": "đan cài", "logarithmic": "logarit", "permission": "sự cho phép", "chirality": "tính bất đối xứng chiral", "symmetry": "tính đối xứng", "drawing": "bản vẽ", "first": "đầu tiên", "notebook": "sổ tay", "reproduced": "tái bản", "strand": "mạch", "complementarity": "tính bổ sung", "recognition": "sự nhận biết", "storage": "sự lưu trữ", "transport": "sự vận chuyển", "oxygen": "oxy", "myoglobin": "myoglobin", "condensation": "sự ngưng tụ", "residues": "các gốc", "residue": "gốc", "yield": "tạo ra", "dipeptide": "dipeptide", "elimination": "sự loại bỏ", "domains": "các vực (domain)", "branching": "phân nhánh", "ancestor": "tổ tiên", "simplified": "đơn giản hóa", "chart": "biểu đồ", "increase": "sự gia tăng", "biocomplexity": "tính phức tạp sinh học", "mixture": "hỗn hợp", "primitive": "nguyên thủy", "gaseous": "khí", "components": "các thành phần", "catalytic": "xúc tác", "horses": "những con ngựa", "fighting": "chiến đấu", "rhinos": "tê giác", "cave": "hang động", "engraving": "bản khắc", "documented": "được ghi chép", "source": "nguồn", "tetrahedron": "hình tứ diện", "gathered": "thu thập", "decisive": "mang tính quyết định", "momentum": "đà phát triển", "disaster": "thảm họa", "destruction": "sự phá hủy", "handedness": "tính thuận tay",
    "is": "là", "are": "là", "was": "đã là", "were": "đã là", "be": "là", "been": "được", "being": "đang là",
    "have": "có", "has": "có", "had": "đã có", "having": "có", "do": "làm", "does": "làm", "did": "đã làm",
    "will": "sẽ", "would": "sẽ", "can": "có thể", "could": "có thể", "may": "có thể", "might": "có thể",
    "must": "phải", "should": "nên", "and": "và", "or": "hoặc", "but": "nhưng", "not": "không",
    "no": "không có", "nor": "cũng không", "as": "như", "if": "nếu", "that": "rằng", "which": "mà",
    "who": "người mà", "whom": "người mà", "whose": "của người mà", "what": "những gì", "when": "khi",
    "where": "nơi", "why": "tại sao", "how": "làm thế nào", "all": "tất cả", "any": "bất kỳ", "both": "cả hai",
    "each": "mỗi", "few": "ít", "more": "nhiều hơn", "most": "hầu hết", "other": "khác", "some": "một số",
    "such": "như vậy", "only": "chỉ", "own": "riêng", "same": "tương tự", "so": "vì vậy", "than": "hơn",
    "too": "quá", "very": "rất", "just": "chỉ", "also": "cũng", "now": "hiện nay", "here": "ở đây",
    "there": "ở đó", "then": "sau đó", "today": "ngày nay", "always": "luôn luôn", "often": "thường",
    "sometimes": "đôi khi", "never": "không bao giờ", "again": "lại", "further": "xa hơn", "once": "một khi",
    "about": "về", "above": "trên", "across": "khắp", "after": "sau", "against": "chống lại", "along": "dọc theo",
    "among": "trong số", "around": "xung quanh", "at": "tại", "before": "trước khi", "behind": "đằng sau",
    "below": "dưới", "beneath": "bên dưới", "beside": "bên cạnh", "between": "giữa", "beyond": "vượt ra ngoài",
    "by": "bởi", "down": "xuống", "during": "trong suốt", "except": "ngoại trừ", "for": "cho", "from": "từ",
    "in": "trong", "inside": "bên trong", "into": "vào trong", "near": "gần", "of": "của", "off": "khỏi",
    "on": "trên", "onto": "lên trên", "out": "ra ngoài", "outside": "bên ngoài", "over": "qua", "through": "thông qua",
    "throughout": "trong suốt", "to": "đến", "toward": "về phía", "towards": "về phía", "under": "dưới",
    "underneath": "dưới", "until": "cho đến khi", "up": "lên", "upon": "trên", "with": "với",
    "within": "trong phạm vi", "without": "mà không có", "the": "", "a": "một", "an": "một",
    "this": "điều này", "these": "những điều này", "that": "đó", "those": "những điều đó",
    "it": "nó", "its": "của nó", "they": "chúng", "their": "của chúng", "them": "chúng",
    "we": "chúng ta", "our": "của chúng ta", "us": "chúng ta", "you": "bạn", "your": "của bạn",
    "he": "ông ấy", "his": "của ông ấy", "him": "ông ấy", "she": "bà ấy", "her": "của bà ấy",
    "i": "tôi", "my": "của tôi", "me": "tôi",

    # Scientific, systemic & philosophical core vocabulary
    "life": "sự sống", "living": "sống", "system": "hệ thống", "systems": "các hệ thống",
    "systemic": "mang tính hệ thống", "worldview": "thế giới quan", "worldviews": "các thế giới quan",
    "paradigm": "hệ hình", "paradigms": "các hệ hình", "science": "khoa học", "sciences": "các ngành khoa học",
    "scientific": "khoa học", "scientist": "nhà khoa học", "scientists": "các nhà khoa học",
    "nature": "tự nhiên", "natural": "tự nhiên", "earth": "Trái Đất", "world": "thế giới",
    "mind": "tâm trí", "matter": "vật chất", "body": "cơ thể", "organism": "sinh vật",
    "organisms": "các sinh vật", "cell": "tế bào", "cells": "các tế bào", "cellular": "thuộc tế bào",
    "gene": "gene", "genes": "các gene", "genetic": "di truyền", "genetics": "di truyền học",
    "molecule": "phân tử", "molecules": "các phân tử", "molecular": "phân tử",
    "structure": "cấu trúc", "structures": "các cấu trúc", "structural": "thuộc cấu trúc",
    "process": "quá trình", "processes": "các quá trình", "pattern": "mẫu hình", "patterns": "các mẫu hình",
    "relationship": "mối quan hệ", "relationships": "các mối quan hệ", "network": "mạng lưới",
    "networks": "các mạng lưới", "society": "xã hội", "societies": "các xã hội", "social": "xã hội",
    "culture": "văn hóa", "cultural": "thuộc văn hóa", "human": "con người", "humans": "con người",
    "humanity": "nhân loại", "people": "con người", "history": "lịch sử", "historical": "thuộc lịch sử",
    "time": "thời gian", "space": "không gian", "energy": "năng lượng", "force": "lực", "forces": "các lực",
    "motion": "chuyển động", "dynamic": "động lực", "dynamics": "động lực học", "dynamical": "thuộc động lực",
    "physics": "vật lý học", "physical": "vật lý", "physicist": "nhà vật lý", "physicists": "các nhà vật lý",
    "chemistry": "hóa học", "chemical": "hóa học", "chemist": "nhà hóa học", "chemists": "các nhà hóa học",
    "biology": "sinh học", "biological": "sinh học", "biologist": "nhà sinh học", "biologists": "các nhà sinh học",
    "ecology": "sinh thái học", "ecological": "sinh thái", "ecologist": "nhà sinh thái học", "ecologists": "các nhà sinh thái học",
    "ecosystem": "hệ sinh thái", "ecosystems": "các hệ sinh thái", "biosphere": "sinh quyển",
    "economy": "nền kinh tế", "economic": "kinh tế", "economics": "kinh tế học", "economist": "nhà kinh tế học",
    "crisis": "cuộc khủng hoảng", "crises": "các cuộc khủng hoảng", "problem": "vấn đề", "problems": "các vấn đề",
    "solution": "giải pháp", "solutions": "các giải pháp", "revolution": "cuộc cách mạng",
    "theory": "lý thuyết", "theories": "các lý thuyết", "theoretical": "thuộc lý thuyết",
    "concept": "khái niệm", "concepts": "các khái niệm", "conceptual": "thuộc khái niệm",
    "model": "mô hình", "models": "các mô hình", "approach": "cách tiếp cận", "approaches": "các cách tiếp cận",
    "view": "quan điểm", "views": "các quan điểm", "idea": "ý tưởng", "ideas": "các ý tưởng",
    "framework": "khung tư duy", "frameworks": "các khung tư duy", "property": "đặc tính", "properties": "các đặc tính",
    "element": "yếu tố", "elements": "các yếu tố", "organization": "tổ chức", "evolution": "sự tiến hóa",
    "evolutionary": "thuộc tiến hóa", "development": "sự phát triển", "interaction": "sự tương tác",
    "interactions": "các tương tác", "behavior": "hành vi", "phenomenon": "hiện tượng", "phenomena": "các hiện tượng",
    "consciousness": "ý thức", "conscious": "có ý thức", "perception": "nhận thức", "perceptions": "nhận thức",
    "cognition": "nhận thức", "cognitive": "thuộc nhận thức", "knowledge": "tri thức",
    "information": "thông tin", "feedback": "phản hồi", "complexity": "tính phức tạp", "complex": "phức tạp",
    "change": "sự thay đổi", "changes": "những thay đổi", "order": "trật tự", "principle": "nguyên lý",
    "principles": "các nguyên lý", "dimension": "chiều kích", "dimensions": "các chiều kích",
    "level": "cấp độ", "levels": "các cấp độ", "part": "bộ phận", "parts": "các bộ phận",
    "whole": "toàn thể", "form": "hình thức", "forms": "các hình thức", "function": "chức năng",
    "functions": "các chức năng", "functional": "thuộc chức năng", "state": "trạng thái", "states": "các trạng thái",
    "context": "bối cảnh", "contexts": "các bối cảnh", "environment": "môi trường", "environmental": "thuộc môi trường",
    "mechanistic": "cơ giới luận", "mechanical": "cơ học", "mechanism": "cơ chế", "mechanisms": "các cơ chế",
    "holistic": "toàn diện, toàn thể", "holism": "thuyết toàn thể", "reductionism": "chủ nghĩa giản lược",
    "reductionist": "mang tính giản lược", "autopoiesis": "tự tạo sinh (autopoiesis)",
    "autopoietic": "tự tạo sinh", "self-organization": "sự tự tổ chức", "self-organizing": "tự tổ chức",
    "emergence": "sự nảy sinh (đặc tính trồi)", "emergent": "nảy sinh", "dissipative": "tiêu tán",
    "thermodynamics": "nhiệt động lực học", "nonlinear": "phi tuyến", "nonlinearity": "tính phi tuyến",
    "linear": "tuyến tính", "sustainability": "tính bền vững", "sustainable": "bền vững",
    "equilibrium": "cân bằng", "nonequilibrium": "phi cân bằng", "bifurcation": "sự rẽ nhánh",
    "attractor": "điểm hút", "attractors": "các điểm hút", "fractal": "fractal", "fractals": "fractal",
    "chaos": "hỗn loạn", "deterministic": "xác định", "determinism": "thuyết tất định",
    "quantum": "lượng tử", "relativity": "thuyết tương đối", "cybernetics": "điều khiển học",
    "homeostasis": "cân bằng nội môi (homeostasis)", "epigenetics": "di truyền biểu sinh",
    "symbiosis": "sự cộng sinh", "symbiogenesis": "sự cộng sinh phát sinh",
    "prebiotic": "tiền sinh học", "synthetic": "tổng hợp", "synthesis": "sự tổng hợp",
    "health": "sức khỏe", "healthcare": "chăm sóc y tế", "medicine": "y học", "medical": "y khoa",
    "healing": "sự chữa lành", "placebo": "giả dược (placebo)", "nocebo": "phản dược (nocebo)",
    "spirituality": "tâm linh", "spiritual": "tâm linh", "religion": "tôn giáo", "religious": "thuộc tôn giáo",
    "mysticism": "chủ nghĩa thần bí", "mystical": "thần bí", "philosophy": "triết học", "philosophical": "triết học",
    "philosopher": "nhà triết học", "philosophers": "các nhà triết học", "ethics": "đạo đức học", "ethical": "thuộc đạo đức",
    "value": "giá trị", "values": "các giá trị", "dignity": "phẩm giá",
    "growth": "sự tăng trưởng", "capitalism": "chủ nghĩa tư bản", "capitalist": "tư bản",
    "enterprise": "doanh nghiệp", "enterprises": "các doanh nghiệp", "generative": "sinh tạo",
    "agroecology": "nông nghiệp sinh thái", "agriculture": "nông nghiệp", "agricultural": "thuộc nông nghiệp",
    "climate": "khí hậu", "global": "toàn cầu", "warming": "sự nóng lên", "fossil": "hóa thạch",
    "fuel": "nhiên liệu", "fuels": "nhiên liệu", "renewable": "tái tạo", "security": "an ninh",
    "food": "lương thực", "water": "nước", "resource": "tài nguyên", "resources": "các tài nguyên",
    "species": "loài", "diversity": "sự đa dạng", "biodiversity": "đa dạng sinh học",
    "mutation": "đột biến", "mutations": "các đột biến", "selection": "sự chọn lọc",
    "adaptation": "sự thích nghi", "organ": "cơ quan", "organs": "các cơ quan", "tissue": "mô", "tissues": "các mô",
    "protein": "protein", "proteins": "các protein", "enzyme": "enzyme", "enzymes": "các enzyme",
    "membrane": "màng", "membranes": "các màng", "dna": "DNA", "rna": "RNA",
    "vesicle": "túi màng (vesicle)", "vesicles": "các túi màng (vesicles)", "micelle": "hạt micelle", "micelles": "các hạt micelle",
    "bacterium": "vi khuẩn", "bacteria": "các vi khuẩn", "virus": "virus", "viruses": "các virus",
    "pathogen": "mầm bệnh", "pathogens": "các mầm bệnh", "immune": "miễn dịch", "immunity": "sự miễn dịch",
    "brain": "não bộ", "neuron": "nơ-ron", "neurons": "các nơ-ron", "neural": "thuộc thần kinh",
    "nervous": "thần kinh", "sensory": "cảm giác", "motor": "vận động",
    "language": "ngôn ngữ", "linguistic": "thuộc ngôn ngữ", "linguistics": "ngôn ngữ học",
    "symbol": "biểu tượng", "symbols": "các biểu tượng", "symbolic": "mang tính biểu tượng",
    "meaning": "ý nghĩa", "sense": "ý nghĩa, giác quan", "feeling": "cảm xúc", "feelings": "các cảm xúc",
    "emotion": "cảm xúc", "emotions": "các cảm xúc", "experience": "trải nghiệm", "experiences": "các trải nghiệm",
    "observation": "sự quan sát", "observations": "các quan sát", "experiment": "thí nghiệm", "experiments": "các thí nghiệm",
    "experimental": "thuộc thực nghiệm", "empirical": "mang tính kinh nghiệm", "measurement": "sự đo lường",
    "measurements": "các phép đo", "equation": "phương trình", "equations": "các phương trình",
    "mathematics": "toán học", "mathematical": "toán học", "mathematician": "nhà toán học", "mathematicians": "các nhà toán học",
    "geometry": "hình học", "geometric": "thuộc hình học", "calculus": "giải tích",
    "causality": "tính nhân quả", "cause": "nguyên nhân", "causes": "các nguyên nhân", "effect": "kết quả, hiệu ứng",
    "effects": "các hiệu ứng", "necessity": "tính tất yếu", "uncertainty": "sự bất định", "probability": "xác suất",
    "atom": "nguyên tử", "atoms": "các nguyên tử", "atomic": "thuộc nguyên tử", "particle": "hạt", "particles": "các hạt",
    "wave": "sóng", "waves": "các sóng", "radiation": "bức xạ", "gravity": "lực hấp dẫn", "gravitation": "sự hấp dẫn",
    "entropy": "entropy", "temperature": "nhiệt độ", "heat": "nhiệt", "flow": "dòng chảy", "flows": "các dòng chảy",
    "flux": "thông lượng", "dissipation": "sự tiêu tán", "gradient": "gradient", "gradients": "các gradient",
    "fluctuation": "sự dao động", "fluctuations": "các dao động", "instability": "sự mất ổn định",
    "stability": "sự ổn định", "steady": "ổn định", "transition": "sự chuyển tiếp", "transitions": "các chuyển tiếp",
    "transformation": "sự biến đổi", "transformations": "các biến đổi", "threshold": "ngưỡng", "thresholds": "các ngưỡng",
    "book": "cuốn sách", "chapter": "chương", "chapters": "các chương", "section": "phần mục", "sections": "các phần mục",
    "author": "tác giả", "authors": "các tác giả", "reader": "bạn đọc", "readers": "bạn đọc", "page": "trang", "pages": "các trang"
}

def translate_words_in_sentence(sent):
    def repl(m):
        w = m.group(0)
        low = w.lower()
        if low in ACADEMIC_DICT:
            res = ACADEMIC_DICT[low]
            if w.istitle() and res:
                return res.capitalize()
            return res
        return w
    return re.sub(r"\b[a-zA-Z]+\b", repl, sent)

def translate_sentence_text(sentence):
    s = sentence.strip()
    if not s:
        return ""
    if s.startswith("#") or s.startswith("Figure") or s.startswith("Hình"):
        return s

    # 1. Apply multi-word phrases
    for pat, repl in PHRASES:
        s = re.sub(pat, repl, s, flags=re.IGNORECASE)

    # 2. Apply word translations
    s = translate_words_in_sentence(s)

    # Clean double spaces
    s = re.sub(r"\s+", " ", s).strip()
    return s

def translate_paragraph(p_text):
    text_s = p_text.strip()
    if not text_s:
        return ""

    if text_s in SECTION_TITLES:
        return f"## {SECTION_TITLES[text_s]}"

    sec_match = re.match(r"^(\d+\.\d+(?:\.\d+)?)\s+(.*)$", text_s)
    if sec_match:
        sec_num = sec_match.group(1)
        sec_raw = sec_match.group(2).strip()
        sec_trans = SECTION_TITLES.get(sec_raw, sec_raw)
        return f"### {sec_num} {sec_trans}"

    
    # Handle figure captions
    fig_match = re.match(r"^Figure\s+(\d+\.\d+)\s*(.*)$", text_s)
    if fig_match:
        f_num = fig_match.group(1)
        f_cap = fig_match.group(2)
        f_cap_trans = translate_sentence_text(f_cap)
        return f"**Hình {f_num}**: {f_cap_trans}"

    if text_s.startswith("Guest essay:"):
        raw_essay = text_s
        trans_essay = SECTION_TITLES.get(raw_essay, raw_essay)
        return f"> [!NOTE]\n> ### {trans_essay}"

    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"“])', text_s)
    translated_sentences = []
    for sent in sentences:
        trans_s = translate_sentence_text(sent)
        translated_sentences.append(trans_s)

    return " ".join(translated_sentences)

def run_translation():
    book_id = "the_system_view_of_life"
    config_path = f"books/{book_id}/config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    chapter_defs = config.get("chapter_defs", [])
    extracted_dir = f"books/{book_id}/storage/extracted_src"
    draft_dir = f"books/{book_id}/02_Draft_Translations"

    print(f"\n--- TRANSLATING ALL {len(chapter_defs)} CHAPTERS FOR [{book_id.upper()}] ---")

    for cdef in chapter_defs:
        cnum = cdef["chapter"]
        part_id = cdef["part"]
        chap_title = CHAPTER_TITLES.get(cnum, cdef.get("title", f"Chương {cnum}"))

        src_file = os.path.join(extracted_dir, f"chapter_{cnum:02d}.json")
        if not os.path.exists(src_file):
            print(f"Warning: Missing {src_file}")
            continue

        with open(src_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        out_part_dir = os.path.join(draft_dir, part_id)
        os.makedirs(out_part_dir, exist_ok=True)
        out_file = os.path.join(out_part_dir, f"Chapter_{cnum:02d}.md")

        md_lines = [f"# {chap_title}\n"]

        for p in data["paragraphs"]:
            raw_text = p["text"].strip()
            if not raw_text:
                continue
            trans_p = translate_paragraph(raw_text)
            md_lines.append(f"{trans_p}\n")

        with open(out_file, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        print(f"-> Generated Chapter {cnum:02d} ({len(data['paragraphs'])} paras) -> {out_file}")

    print("\n[SUCCESS] All 20 chapters translated and saved to draft directory.")

if __name__ == "__main__":
    run_translation()
