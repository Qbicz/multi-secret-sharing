CXXFLAGS =	-O2 -g -Wall -fmessage-length=0 -std=c++11

OBJS =		main-multi-secret.o

LIBS =

TARGET =	main-multi-secret

$(TARGET):	$(OBJS)
	$(CXX) -o $(TARGET) $(OBJS) $(LIBS)

all:	$(TARGET)

clean:
	rm -f $(OBJS) $(TARGET)
